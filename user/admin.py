from django.contrib import admin
from user.models import UserProfile


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_phone', 'user_address')
    search_fields = ('user',)