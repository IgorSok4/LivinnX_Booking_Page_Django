from datetime import datetime, timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from account.models import Profile
from .forms import AdminLoginForm, PageNumberForm, TenantEditForm
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

    
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request,
                  'management/admin_dashboard.html')
    
    
@user_passes_test(lambda u: u.is_staff)
def admin_tenants(request):
    all_users = Profile.objects.all().order_by('id')
    paginator = Paginator(all_users, 25)

    if request.method == 'POST':
        form = PageNumberForm(request.POST)
        if form.is_valid():
            page = form.cleaned_data['page']
            return redirect('admin_tenants', page=page)
    else:
        form = PageNumberForm()

    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request,
                  'management/admin_tenants.html',
                  {'users': users,
                   'page': page,
                   'page_num': paginator.num_pages,
                   'form': form})

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TenantsListView(ListView):
    queryset = Profile.objects.all()
    context_object_name = 'users'
    paginate_by = 25
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

from django.shortcuts import redirect  # Importuj redirect

@user_passes_test(lambda u: u.is_staff)
def admin_tenant_profile(request, user_id, name, surname):
    todays_date = datetime.now().date()
    tomorrows_date = todays_date + timedelta(days=1)
    user = Profile.objects.get(id=user_id)
    user_reservations = UserReservation.objects.filter(user=user.user)
    amenities = Amenity.objects.all()

    tenant_edit_form = TenantEditForm(instance=user.user)
    
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

    if request.method == 'POST':
        if 'user_profile' in request.POST:
            print("user_profile in request.POST")
            tenant_edit_form = TenantEditForm(request.POST, instance=user.user)

            if tenant_edit_form.is_valid():
                tenant_edit_form.save()
                return redirect('admin_tenant_profile', user_id=user_id, name=name, surname=surname)

    user = Profile.objects.get(id=user_id)

    return render(request, 'management/admin_tenant_profile.html', {
        'tenant_edit_form': tenant_edit_form,
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

