from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from datetime import date


class Hotel(models.Model):
    hotel_image = models.ImageField(upload_to='hotel_photos', blank=True, null=True, default='hotel_def.jpg')
    hotel_star = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    hotel_contact = models.CharField(max_length=30, blank=True)
    hotel_name = models.CharField(max_length=40, unique=True)
    hotel_address = models.CharField(max_length=60)
    hotel_email = models.EmailField(blank=True)
    hotel_about = models.TextField(blank=True)

    def __str__(self):
        return self.hotel_name

    class Meta:
        verbose_name_plural = 'Hotels'
        db_table = 'Hotels'
        ordering = ['hotel_name']


class Room(models.Model):
    room_image = models.ImageField(upload_to='room_photos', blank=True, null=True, default='room_def.jpg')
    room_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_available = models.BooleanField(default=True)
    room_type = models.CharField(max_length=30)
    room_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Type - {self.room_type}, Room - {self.room_number}, Hotel - {self.hotel.hotel_name}"

    class Meta:
        db_table = 'Rooms'
        verbose_name_plural = 'Rooms'
        ordering = ['hotel', 'room_number']
        unique_together = ('hotel', 'room_number')


class RoomImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_carusel')
    images = models.ImageField(upload_to='room_carusel')

    def __str__(self):
        return f"room {self.room.room_type}'s images"


class HotelsImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_carusel')
    images = models.ImageField(upload_to='hotel_carusel')

    def __str__(self):
        return f"hotel {self.hotel.hotel_name}'s images"


class Reservation(models.Model):
    STATUS_CHOICE = (('active', 'active'), ('completed', 'completed'), ('canceled', 'canceled'), ('upcoming', 'upcoming'))
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICE, default='active')
    check_out = models.DateField()
    check_in = models.DateField()

    class Meta:
        verbose_name_plural = 'Reservations'
        db_table = 'Reservations'
        ordering = ['check_in']

    def __str__(self):
        return f"user: {self.user.username}, room: {self.room.room_type}, hotel: {self.hotel.hotel_name}, date: {self.check_in} - {self.check_out}"

    def clean(self):
        super().clean()
        if self.status == 'canceled':
            return
        if not self.room_id:
            return

        today = date.today()
        if self.check_in >= self.check_out:
            raise ValidationError({'check_out': _('Check-out must be after check-in day.')})
        elif self.check_in < today:
            raise ValidationError({'check_in': _('Check-in must be today or in the future.')})

        already_booked = Reservation.objects.filter(
            room=self.room,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
            status__in = ['active', 'upcoming']
        ).exclude(pk=self.pk)

        if already_booked.exists():
            raise ValidationError('This room is already booked on these dates')

    def canceled(self):
        self.status = 'canceled'
        self.save()
        self.room.room_available = True
        self.room.save()

    def save(self, *args, **kwargs):
        if not self.room_id:
            return super().save(*args, **kwargs)
        self.clean()
        today = date.today()
        nights = (self.check_out - self.check_in).days
        self.total_price = nights * self.room.room_price

        if self.status != 'canceled':
            if self.check_out < today:
                self.status = 'completed'
            elif self.check_in <= today <= self.check_out:
                self.status = 'active'
            else: self.status = 'upcoming'

        super().save(*args, **kwargs)

        if self.status in ['active', 'upcoming']:
            self.room.room_available = False
        else:
            self.room.room_available = True
        self.room.save(update_fields=['room_available'])