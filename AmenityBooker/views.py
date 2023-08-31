from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .models import Amenity, ReservationModel, Hour, UserReservation
from .forms import ReservationForm
from account.models import Profile


def process_reservation(user, amenity_slug, amenity_date_str, selected_hours_str_today, selected_hours_str_tomorrow):

    amenity_date = datetime.strptime(amenity_date_str, '%Y-%m-%d').date()

    selected_hours_today = [hour for hour in selected_hours_str_today.split(',') if hour]
    selected_hours_tomorrow = [hour for hour in selected_hours_str_tomorrow.split(',') if hour]

    if len(selected_hours_today) > 4:
        return {"status": "failed", "message": "You cannot select more than 4 hour blocks for today."}

    if len(selected_hours_tomorrow) > 4:
        return {"status": "failed", "message": "You cannot select more than 4 hour blocks for tomorrow."}

    # Handle reservation for today
    if len(selected_hours_today) > 0:
        reservation_today = ReservationModel.objects.filter(amenity__slug=amenity_slug, date=amenity_date).first()
        
        if reservation_today:
            hours_today = Hour.objects.filter(start_end_time__in=selected_hours_today)
            if not all(hour in reservation_today.hours_available_today.all() for hour in hours_today):
                return {"status": "failed", "message": "One or more of the selected hours for today are not available."}
            reservation_today.hours_booked_today.add(*hours_today)
            reservation_today.hours_available_today.remove(*hours_today)
            reservation_today.save()
            user_reservation_today = UserReservation.objects.create(user=user, amenity=reservation_today.amenity, date=amenity_date)
            for hour in hours_today:
                user_reservation_today.hours_booked.add(hour)

    # Handle reservation for tomorrow
    if len(selected_hours_tomorrow) > 0:
        amenity_date_tomorrow = amenity_date + timedelta(days=1)
        reservation_tomorrow = ReservationModel.objects.filter(amenity__slug=amenity_slug, date=amenity_date).first()
        if reservation_tomorrow:
            hours_tomorrow = Hour.objects.filter(start_end_time__in=selected_hours_tomorrow)
            if not all(hour in reservation_tomorrow.hours_available_tomorrow.all() for hour in hours_tomorrow):
                return {"status": "failed", "message": "One or more of the selected hours for tomorrow are not available."}
            reservation_tomorrow.hours_booked_tomorrow.add(*hours_tomorrow)
            reservation_tomorrow.hours_available_tomorrow.remove(*hours_tomorrow)
            reservation_tomorrow.save()
            user_reservation_tomorrow = UserReservation.objects.create(user=user, amenity=reservation_tomorrow.amenity, date=amenity_date_tomorrow)
            for hour in hours_tomorrow:
                user_reservation_tomorrow.hours_booked.add(hour)
                
    return {"status": "success"}




@login_required
def make_reservation(request):
    if request.method == "POST":
        response = process_reservation(
            user=request.user,
            amenity_slug=request.POST['amenity_slug'],
            amenity_date_str=request.POST['amenity_date'],
            selected_hours_str_today=request.POST['hours_today'],
            selected_hours_str_tomorrow=request.POST['hours_tomorrow']
        )
        return JsonResponse(response)
    
    
@method_decorator(login_required, name='dispatch')
class AmenitiesListView(ListView):
    template_name = 'reservation/amenity_list.html'
    model = Amenity
    context_object_name = 'amenities'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today().date()
        context['today'] = today
        return context
    
    
    
@method_decorator(login_required, name='dispatch')
class AmenityDetailView(View):
    template_name = 'reservation/reservation_detail.html'
    slug_url_kwarg = 'amenity_slug'
    date_url_kwarg = 'amenity_date'

    def get_object(self, amenity_slug, amenity_date_str):
        amenity_date = datetime.strptime(amenity_date_str, '%Y-%m-%d').date()
        return ReservationModel.objects.get(amenity__slug=amenity_slug, date=amenity_date)

    def get(self, request, *args, **kwargs):
        user = Profile.objects.get(user=request.user)
        amenity_slug = self.kwargs[self.slug_url_kwarg]
        amenity_date_str = self.kwargs[self.date_url_kwarg]
        amenity = Amenity.objects.get(slug=amenity_slug)
        reservation = self.get_object(amenity_slug, amenity_date_str)
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)
        user_active = user.active
        amenity_active_attribute = f"{amenity_slug}_active"
        user_active_amenity = getattr(user, amenity_active_attribute)

        user_reservations_today = UserReservation.objects.filter(user=request.user, 
                                                            date=today,
                                                            amenity__slug=amenity_slug)
        hours_booked_today = []
        for res in user_reservations_today:
            hours_booked_today.extend(list(res.hours_booked.all()))
            
            
        user_reservations_tomorrow = UserReservation.objects.filter(user=request.user, 
                                                            date=tomorrow,
                                                            amenity__slug=amenity_slug)
        hours_booked_tomorrow = []
        for res in user_reservations_tomorrow:
            hours_booked_tomorrow.extend(list(res.hours_booked.all()))
    

        context = {
            'object': reservation,
            'amenity': amenity,
            'form': ReservationForm(),
            'tomorrow': reservation.date + timedelta(days=1),
            'today': today,
            'hours_booked_today': hours_booked_today,
            'hours_booked_tomorrow': hours_booked_tomorrow,
            'user_active': user_active,
            'user_active_amenity': user_active_amenity,
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        response = process_reservation(
            user=request.user,
            amenity_slug=self.kwargs['amenity_slug'],
            amenity_date_str=self.kwargs['amenity_date'],
            selected_hours_str_today=request.POST['hours_today'],
            selected_hours_str_tomorrow=request.POST['hours_tomorrow']
        )
        
        if response["status"] == "success":
            messages.success(request, "Your reservation was successful.")
            return HttpResponseRedirect(reverse('amenity_detail', args=[self.kwargs['amenity_slug'], self.kwargs['amenity_date']]))
        else:
            messages.error(request, response["message"])
            return HttpResponseBadRequest(response["message"])
    
    
    
