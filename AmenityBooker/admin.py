from django.contrib import admin
from .models import Images, Hour, BookedHour, Amenity, ReservationModel, UserReservation

# class AmenityReservationAdmin(admin.ModelAdmin):
#     list_display = ('amenity', 'user', 'reservation_time_periods_list',)
#     list_filter = ('amenity', 'user',)
    
#     def reservation_time_periods_list(self, obj):
#         return ", ".join([str(time_period) for time_period\
#                          in obj.reservation_time_periods.all()])
#     reservation_time_periods_list.short_description = 'Time periods'

# admin.site.register(AmenityTime)
# admin.site.register(Amenity)
# admin.site.register(AmenityReservation, AmenityReservationAdmin)
admin.site.register(Hour)
admin.site.register(BookedHour)

@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('file',)
    
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ['name']}

@admin.register(ReservationModel)
class ReservationModelAdmin(admin.ModelAdmin):
    list_display = ('amenity', 'date',)
    
    
@admin.register(UserReservation)
class UserReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amenity', 'user_reservation_time_periods_list')
    
    def user_reservation_time_periods_list(self, obj):
        return ", ".join([str(time_period) for time_period\
                        in obj.hours_booked.all()])
    user_reservation_time_periods_list.short_description = 'Time periods'
