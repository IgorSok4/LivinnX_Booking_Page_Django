from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from blog.models import Post
from django.contrib import messages

from .forms import LoginForm, UserRegistrationForm, UserEditForm
from .models import Profile
from AmenityBooker.models import UserReservation, ReservationModel



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'latest_posts': Post.objects.filter(status="published")[:12]})
    
    
@login_required
def profile(request):
    todays_date = datetime.now().date()
    tomorrows_date = todays_date + timedelta(days=1)
    user_profile = Profile.objects.get(user=request.user)
    user_reservations = UserReservation.objects.filter(user=request.user)
    return render(request,
                  'account/profile.html',
                  {'user_profile': user_profile,
                   'user_reservations': user_reservations,
                   'todays_date': todays_date,
                   'tomorrows_date': tomorrows_date,
                   'section': 'user_profile'})


@login_required
def reservation_delete(request, reservation_id):
    reservation = get_object_or_404(UserReservation, id=reservation_id)
    if request.user == reservation.user:
        if request.method == "POST":
            today_date = datetime.today().date()  # Pobierz aktualną datę
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
            return redirect('user_profile')

    
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.success(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form})
    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password'])
            new_user.save()
            new_profile = Profile.objects.create(user=new_user, id=new_user.id)
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user,
                           'new_profile': new_profile})
    
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})
