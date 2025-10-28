from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from hotel_app.forms import BookingForm
from hotel_app.models import Room, Hotel, Reservation


class IndexView(ListView):
    model = Room
    template_name = 'index.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        rooms = Room.objects.all()
        search = self.request.GET.get('q')
        if search:
            rooms = rooms.filter(Q(room_type__icontains=search) | Q(hotel__hotel_name__icontains=search)).distinct()
        return rooms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorite_rooms'] = Room.objects.filter(room_price__gt=200, room_available=True).order_by('-room_price')[:4]
        return context


class HotelsView(ListView):
    model = Hotel
    template_name = 'hotels.html'
    context_object_name = 'hotels'
    paginate_by = 4


class HotelDetail(DetailView):
    model = Hotel
    template_name = 'hotel_detail.html'
    context_object_name = 'hotel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.filter(hotel=self.object, room_available=True)
        context['images'] = self.object.hotel_carusel.all()
        return context


class AllRooms(ListView):
    model = Room
    template_name = 'rooms.html'
    context_object_name = 'rooms'
    paginate_by = 8

    def get_queryset(self):
        rooms = Room.objects.filter(room_available=True)
        search = self.request.GET.get('q', '').strip()
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        room_type = self.request.GET.get('room_type')
        hotel_name = self.request.GET.get('hotel_name')
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')

        if search:
            rooms = rooms.filter(Q(room_type__icontains=search) | Q(hotel__hotel_name__icontains=search)).distinct()
        if min_price:
            rooms = rooms.filter(room_price__gte=min_price)
        if max_price:
            rooms = rooms.filter(room_price__lte=max_price)
        if room_type:
            rooms = rooms.filter(room_type__icontains=room_type)
        if hotel_name:
            rooms = rooms.filter(hotel__hotel_name__icontains=hotel_name)
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

                reserved_rooms = Reservation.objects.filter(
                    Q(check_in__lt=check_out_date) & Q(check_out__gt=check_in_date)
                ).values_list('room_id', flat=True)

                rooms = rooms.exclude(id__in=reserved_rooms)
            except ValueError:
                pass
        return rooms


class RoomDetail(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        context['hotel'] = room.hotel
        context['images'] = room.room_carusel.all()
        context['available'] = room.room_available
        if self.request.user.is_authenticated:
            context['user_reservations'] = room.reservations.filter(user=self.request.user)
        else:
            context['user_reservations'] = None
        return context

class ReservationView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = BookingForm
    template_name = 'booking.html'
    success_url = reverse_lazy('user:profile')
    login_url = 'user:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('room_id')
        context['hotels'] = Hotel.objects.all()

        if room_id:
            room = get_object_or_404(Room, pk=room_id)
            context['room'] = room
            context['hotel'] = room.hotel
        else:
            context['room'] = None
            context['rooms'] = Room.objects.filter(room_available=True)
            context['hotel'] = None
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ['POST', 'GET']:
            hotel_id = self.request.POST.get('hotel') or self.request.GET.get('hotel')
            if hotel_id:
                kwargs['hotel_id'] = hotel_id
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        room_id = self.kwargs.get('room_id')

        if room_id:
            room = get_object_or_404(Room, pk=room_id)
            initial['room'] = room
            initial['hotel'] = room.hotel
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        room_id = self.kwargs.get('room_id')

        if room_id:
            room = get_object_or_404(Room, pk=room_id)
        else:
            room = form.cleaned_data.get('room')

        if not room:
            form.add_error('room', 'Please select a room.')
            return self.form_invalid(form)

        if not room.room_available:
            form.add_error('room', 'This room is already booked.')
            return self.form_invalid(form)

        form.instance.room = room
        form.instance.hotel = room.hotel

        return super().form_valid(form)

def hotel_rooms(request):
    hotel_id = request.GET.get('hotel_id')
    rooms = Room.objects.filter(hotel_id=hotel_id, room_available=True)
    html = '<option value="">---------</option>'
    for room in rooms:
        html += f'<option value="{room.id}">Room Type: {room.room_type} - Room Number: {room.room_number}</option>'
    return HttpResponse(html)


class CancelView(LoginRequiredMixin, View):
    def post(self, request, id):
        reservation = get_object_or_404(Reservation, pk=id, user=request.user)

        if reservation.status != 'canceled':
            reservation.canceled()
            messages.success(request, 'Reservation successfully canceled!')
        else:
            messages.warning(request, 'This reservation is already canceled!')

        return redirect('user:profile')
