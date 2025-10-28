from django import forms
from django.forms import models

from hotel_app.models import Reservation, Room


class BookingForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['hotel', 'room', 'guests', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id',None)
        if 'data' in kwargs:
            data = kwargs['data']
            hotel_id = data.get('hotel') or data.get('hotel_id')
        super().__init__(*args, **kwargs)

        if hotel_id:
            self.fields['room'].queryset = Room.objects.filter(hotel_id=hotel_id, room_available=True)
        else:
            self.fields['room'].queryset = Room.objects.none()
