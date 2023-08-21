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


@login_required
def make_reservation(request):
    if request.method == "POST":
        user = request.user
        amenity_slug = request.POST['amenity_slug']
        amenity_date_str = request.POST['amenity_date']
        amenity_date = datetime.strptime(amenity_date_str, '%Y-%m-%d').date()

        selected_hours_str = request.POST['hours']
        selected_hours = selected_hours_str.split(',')
        reservation = ReservationModel.objects.get(amenity__slug=amenity_slug, date=amenity_date)

        hours = Hour.objects.filter(start_end_time__in=selected_hours)

        if len(hours) > 4:
            return JsonResponse({"status": "failed", "message": "You cannot select more than 4 hour blocks."})

        if not all(hour in reservation.hours_available_today.all() for hour in hours):
            return JsonResponse({"status": "failed", "message": "One or more of the selected hours are not available."})

        reservation.hours_booked_today.add(*hours)
        reservation.hours_available_today.remove(*hours)
        reservation.save()

        try:
            user_reservation = UserReservation.objects.create(user=user, amenity=reservation.amenity, date=amenity_date)
            user_reservation.hours_booked.add(*hours)
            user_reservation.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "failed", "message": f"Reservation failed: {str(e)}"})


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
        reservation = self.get_object(amenity_slug, amenity_date_str)
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)
        user_active = user.active

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
            'form': ReservationForm(),
            'tomorrow': reservation.date + timedelta(days=1),
            'today': today,
            'hours_booked_today': hours_booked_today,
            'hours_booked_tomorrow': hours_booked_tomorrow,
            'user_active': user_active,
        }

        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        user = request.user
        amenity_slug = self.kwargs['amenity_slug']
        amenity_date_str = self.kwargs['amenity_date']
        amenity_date = datetime.strptime(amenity_date_str, '%Y-%m-%d').date()

        # get the hours from the form submission
        selected_hours_str = request.POST['hours']
        selected_hours = selected_hours_str.split(',')
        # retrieve the relevant ReservationModel
        reservation = ReservationModel.objects.get(amenity__slug=amenity_slug, date=amenity_date)

        # retrieve the hours instances based on the submitted hours
        hours = Hour.objects.filter(start_end_time__in=selected_hours)

        # check amount of hour blocks that user has booked already
        if len(hours) > 4:
            return HttpResponseBadRequest('You cannot select more than 4 hour blocks.')

        # check if all selected hours are available
        if not all(hour in reservation.hours_available_today.all() for hour in hours):
            return HttpResponseBadRequest('One or more of the selected hours are not available.')

        # book the hours
        reservation.hours_booked_today.add(*hours)
        reservation.hours_available_today.remove(*hours)
        reservation.save()

        # add user reservation
        try:
            user_reservation = UserReservation.objects.create(user=user, amenity=reservation.amenity, date=amenity_date)
            user_reservation.hours_booked.add(*hours)
            user_reservation.save()
            messages.success(request, "Your reservation was successful.")
        except Exception as e:
            messages.error(request, f"Reservation failed: {e}")

        return HttpResponseRedirect(reverse('amenity_detail', args=[amenity_slug, amenity_date_str]))


