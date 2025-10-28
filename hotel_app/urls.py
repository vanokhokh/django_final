from hotel_app.views import IndexView, HotelsView, HotelDetail, AllRooms, RoomDetail, ReservationView, CancelView
from django.urls import path
from . import views

app_name = 'hotel_app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('hotels/', HotelsView.as_view(), name='hotel'),
    path('hotels/<int:pk>/', HotelDetail.as_view(), name='hotel_detail'),

    path('rooms/', AllRooms.as_view(), name='all_rooms'),
    path('rooms/<int:pk>/', RoomDetail.as_view(), name='room_detail'),

    path('booking/', ReservationView.as_view(), name='booking_random'),
    path('booking/<int:room_id>/', ReservationView.as_view(), name='booking'),
    path('ajax/hotel_rooms/', views.hotel_rooms, name='hotel_rooms'),

    path('cancel/<int:id>/', CancelView.as_view(), name='cancel'),
]