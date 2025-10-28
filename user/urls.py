from django.urls import path
from user.views import UserCreate, UserLogin, UserLogout, UserProfileView
app_name = 'user'

urlpatterns = [
    path('registration/', UserCreate.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile')
]