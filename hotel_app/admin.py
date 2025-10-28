from hotel_app.models import Hotel, Reservation, Room, RoomImages, HotelsImages
from django.contrib import admin


class HotelsImageInline(admin.TabularInline):
    model = HotelsImages
    extra = 1
    max_num = 10

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    search_fields = ('hotel_name', 'hotel_address')
    list_display = ('hotel_name', 'hotel_address')
    inlines = [HotelsImageInline]


class RoomImageInline(admin.TabularInline):
    model = RoomImages
    extra = 1
    max_num = 10

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'room_number', 'hotel', 'room_price', 'room_available')
    list_filter = ('hotel', 'room_available', 'room_type')
    search_fields = ('room_type', 'hotel__hotel_name')
    inlines = [RoomImageInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
     list_display = ('user', 'hotel', 'room', 'check_in', 'check_out', 'total_price')
     list_filter = ('hotel', 'room', 'check_in')
     readonly_fields = ('total_price',)