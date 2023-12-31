from datetime import datetime, timedelta, date

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from account.models import Profile, Comment
from AmenityBooker.models import Amenity
from .forms import AdminLoginForm, PageNumberForm, TenantEditForm, CommentForm, SearchForm
from AmenityBooker.models import UserReservation, ReservationModel, Amenity


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('/admin/dashboard/')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.info(request, 'Account not found')
                return redirect(reverse('admin_login'))

            user = authenticate(request, username=username, password=password)

            if user and user.is_staff:
                login(request, user)
                return redirect('/admin/dashboard/')

            messages.info(request, 'Invalid password')
            return redirect(reverse('admin_login'))

    else:
        form = AdminLoginForm()

    return render(request, 'management/login_admin.html', {'form': form})


def hour_start_time(hour_string):
    hour_string = str(hour_string)
    start_time_str = hour_string.split('-')[0]
    return datetime.strptime(start_time_str, '%H:%M').time()

def hour_start_end_time(hour_start, hour_end):
    """
    Converts hour strings in the format 'HH:MM-HH:MM' to datetime.time objects.
    Parameters:
    hour_start (str): The starting time in 'HH:MM' format.
    hour_end (str): The ending time in 'HH:MM' format.
    Returns: A tuple containing the starting and ending times as datetime.time objects.
    """
    hour_start = str(hour_start)
    hour_end = str(hour_end)
    start_time_str = hour_start.split('-')[0]
    end_time_str = hour_end.split('-')[1]

    return datetime.strptime(start_time_str, '%H:%M').time(),\
           datetime.strptime(end_time_str, '%H:%M').time()

def is_current_reservation(hours_booked, date):
    current_datetime = datetime.now()
    start_time, end_time = hour_start_end_time(hours_booked.first(), hours_booked.last())

    if current_datetime.date() == date:
        if start_time <= end_time:
            return start_time <= current_datetime.time() <= end_time
        else:
            return start_time <= current_datetime.time() or current_datetime.time() <= end_time
    
    return False



@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    amenities = Amenity.objects.all()
    latest_reservations = UserReservation.objects.all().order_by('-id')[:10]
    incoming_reservations = UserReservation.objects.all().order_by('-date')[:10]
    current_reservations = UserReservation.objects.all().order_by('-date')[:10]
    current_datetime = datetime.now()
    
    current_reservations = [
        r for r in current_reservations if is_current_reservation(r.hours_booked, r.date)
    ]
    
    incoming_reservations = [
        r for r in incoming_reservations
        if r.date >= date.today() and (
            any(
                current_datetime < datetime.combine(r.date, hour_start_time(hour_block))
                for hour_block in r.hours_booked.all()[:1]
            ) or r.date > date.today())]

    incoming_reservations = sorted(
        incoming_reservations,
        key=lambda r: min(
            abs((datetime.combine(r.date, hour_start_time(hour_block)) - current_datetime))
            for hour_block in r.hours_booked.all()[:1]
        )
    )
    
    for reservation in incoming_reservations:
        for hour_block in reservation.hours_booked.all()[:1]:
            seconds = abs((datetime.combine(reservation.date, hour_start_time(hour_block)) - current_datetime).seconds)

    return render(request,
                  'management/admin_dashboard.html',
                  {'amenities': amenities,
                   'latest_reservations' : latest_reservations,
                   'incoming_reservations': incoming_reservations,
                   'current_reservations' : current_reservations,
                   })
    
    
@user_passes_test(lambda u: u.is_staff)
def admin_amenity_active(request, amenity_id):
    amenity = get_object_or_404(Amenity, id=amenity_id)
    user = request.user

    if request.method == "POST":
        if user.is_superuser:
            amenity.available = not amenity.available
            amenity.save()
            return redirect('admin_dashboard')
        else:
            response_data = {
                "message": "You don't have permission.",
                "success": False
            }
            return JsonResponse(response_data, status=403)
    else:
        return HttpResponseNotAllowed(['POST'])
    

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TenantsListView(ListView):
    queryset = Profile.objects.all()
    context_object_name = 'users'
    paginate_by = 3
    template_name = 'management/admin_tenants.html'


def toggle_user_active(request, user_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            user = Profile.objects.get(id=user_id)
            user.active = not user.active
            user.save()
            return JsonResponse({'success': True})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@user_passes_test(lambda u: u.is_staff)
def tenant_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = User.objects.annotate(
                similarity=TrigramSimilarity('first_name', query) + TrigramSimilarity('last_name', query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request, 'management/admin_tenant_search.html',
                  {'form': form, 
                   'query': query, 
                   'results': results,
                   'results_count': len(results),})


@user_passes_test(lambda u: u.is_staff)
def admin_tenant_profile(request, user_id, name, surname):
    todays_date = datetime.now().date()
    tomorrows_date = todays_date + timedelta(days=1)
    user = Profile.objects.get(id=user_id)
    user_reservations = UserReservation.objects.filter(user=user.user)
    amenities = Amenity.objects.all()
    comments = Comment.objects.filter(user=user.user)
    
    amenities_active = {
        'amenities_details': [
            {'name': 'Sauna', 'active': user.sauna_active},
            {'name': 'Jacuzzi', 'active': user.jacuzzi_active},
            {'name': 'Orange', 'active': user.orange_active},
            {'name': 'Blue', 'active': user.blue_active},
            {'name': 'Music', 'active': user.music_active},
            {'name': 'Art', 'active': user.art_active},
        ]
    }
    
    tenant_edit_form = TenantEditForm(instance=user.user)
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'user_profile' in request.POST:
            tenant_edit_form = TenantEditForm(request.POST, instance=user.user)

            if tenant_edit_form.is_valid():
                tenant_edit_form.save()
                return redirect('admin_tenant_profile', user_id=user_id, name=name, surname=surname)
        
        if 'user_comments' in request.POST:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.user = user.user
                new_comment.save()
            else:
                comment_form = CommentForm()

    user = Profile.objects.get(id=user_id)

    return render(request, 'management/admin_tenant_profile.html', {
        'tenant_edit_form': tenant_edit_form,
        'comments': comments,
        'comment_form': comment_form,
        'user': user,
        'user_reservations': user_reservations,
        'todays_date': todays_date,
        'tomorrows_date': tomorrows_date,
        'amenities': amenities,
        'amenities_active': amenities_active,
    })

@user_passes_test(lambda u: u.is_staff)
def reservation_delete(request, reservation_id):
    reservation = get_object_or_404(UserReservation, id=reservation_id)
    user = reservation.user
    if user == reservation.user:
        if request.method == "POST":
            today_date = datetime.today().date()
            hours_to_return = reservation.hours_booked.all()
            reservation_model = ReservationModel.objects.get(date=today_date, amenity=reservation.amenity)
            
            if reservation.date == today_date:
                for hour in hours_to_return:
                    reservation_model.hours_available_today.add(hour)
                    reservation_model.hours_booked_today.remove(hour)
                    
            elif reservation.date == today_date + timedelta(days=1):
                for hour in hours_to_return:
                    reservation_model.hours_available_tomorrow.add(hour)
                    reservation_model.hours_booked_tomorrow.remove(hour)

            reservation.delete()
            return redirect('admin_dashboard')
        else:
            return HttpResponseNotAllowed(['POST'])
    else:
        return HttpResponse("You don't have permission to delete this reservation.")
    

def toggle_reservation_active(request, reservation_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            reservation = UserReservation.objects.get(id=reservation_id)
            reservation.active = not reservation.active
            reservation.save()
            return JsonResponse({'success': True})
        except UserReservation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Reservation not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@user_passes_test(lambda u: u.is_staff)
def admin_tenant_amenity_active(request, user_id, amenity_slug):
    user_main = User.objects.get(id=user_id)
    user_profile = Profile.objects.get(id=user_id)
    user_admin = request.user

    amenity_active_attribute = f"{amenity_slug}_active"
    user_active_amenity = getattr(user_profile, amenity_active_attribute)

    if request.method == "POST":
        if user_admin.is_superuser:
            setattr(user_profile, amenity_active_attribute, not user_active_amenity)
            user_profile.save()
            return redirect('admin_tenant_profile', name=user_main.first_name, surname=user_main.last_name, user_id=user_id)
        else:
            response_data = {
                "message": "You don't have permission.",
                "success": False
            }
            return JsonResponse(response_data, status=403)
    else:
        return HttpResponseNotAllowed(['POST'])



def delete_comment(request, user_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user == request.user.is_staff or request.user.is_superuser:
        comment.delete()
        
    return redirect('admin_tenant_profile', user_id=user_id, name=comment.user.first_name, surname=comment.user.last_name)

