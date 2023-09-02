from celery import shared_task
from datetime import date, timedelta
from AmenityBooker.models import ReservationModel, Amenity

@shared_task
def create_daily_reservations():
    all_amenities = Amenity.objects.all()
    today = date.today()
    
    for amenity in all_amenities:
        available_hours = amenity.hours.all()
    
        previous_reservation = ReservationModel.objects.filter(amenity=amenity, 
                                                               date=today - timedelta(days=1)).first()
        # if reservationmodel for today does not exists, created today = True
        reservation_today, created_today = ReservationModel.objects.get_or_create(
            amenity=amenity,
            date=today
        )
        if created_today:
            # When we enter a new day, the hours available 'tomorrow' from previous ReservationModel become the hours available 'today'.
            if previous_reservation: 
                reservation_today.hours_available_today.set(previous_reservation.hours_available_tomorrow.all())
                reservation_today.hours_booked_today.set(previous_reservation.hours_booked_tomorrow.all())
            else:
                reservation_today.hours_available_today.set(available_hours)
                reservation_today.hours_available_tomorrow.set(available_hours)
