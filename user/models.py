from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_phone = models.CharField(max_length=20, blank=True, null=True)
    user_address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

