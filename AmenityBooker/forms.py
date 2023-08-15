from django import forms
from .models import UserReservation, Hour

class ReservationForm(forms.ModelForm):
    hours_booked = forms.ModelMultipleChoiceField(
        queryset=Hour.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = UserReservation
        fields = ['amenity', 'date', 'hours_booked']