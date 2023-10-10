from django.db import models
from django.contrib.auth.models import User

class Images(models.Model):
    file = models.ImageField(upload_to='amenities')
    
class Hour(models.Model):
    start_end_time = models.CharField(max_length=40)
    
    def __str__(self):
        return f"{self.start_end_time}"
    
class BookedHour(models.Model):
    start_end_time = models.CharField(max_length=40)
    
    def __str__(self):
        return f"{self.start_end_time}"

class Amenity(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=40)
    description = models.CharField(max_length=200)
    regulations = models.TextField()
    opening_hours = models.TextField()
    images = models.ManyToManyField(Images)
    hours = models.ManyToManyField(Hour)
    available = models.BooleanField(default=True)
    additional_info = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.name}"

class ReservationModel(models.Model):
    amenity = models.ForeignKey(Amenity,
                                on_delete=models.CASCADE)
    date = models.DateField()
    hours_available_today =  models.ManyToManyField(Hour,
                                    related_name='hours_available_today',
                                    blank=True)
    hours_booked_today = models.ManyToManyField(Hour,
                                    related_name='hours_booked_today',
                                    blank=True)
    hours_available_tomorrow = models.ManyToManyField(Hour,
                                    related_name='hours_available_tomorrow',
                                    blank=True)
    hours_booked_tomorrow = models.ManyToManyField(Hour,
                                    related_name='hours_booked_tomorrow',
                                    blank=True)
    
    def __str__(self):
        return f"{self.amenity} | {self.date}"
    
class UserReservation(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity,
                                on_delete=models.CASCADE)
    date = models.DateField()
    hours_booked = models.ManyToManyField(Hour)
    active = models.BooleanField(default=True)
    
    def split_start_end_time(self, start_end_time):
        start_time, end_time = start_end_time.split('-')
        return start_time, end_time

    def reservation_period(self):
        hours = self.hours_booked.all()
        if hours.exists():
            start_time = self.split_start_end_time(hours.first().start_end_time)[0]
            last_end_time = self.split_start_end_time(hours.last().start_end_time)[1]
            return start_time, last_end_time
        return None
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.email} | {self.date}"
