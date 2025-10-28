from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Case, When, IntegerField
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView

from hotel_app.models import Reservation
from user.forms import CreateUserForm, UserProfileForm
from user.models import UserProfile


class UserCreate(CreateView):
    model = User
    form_class = CreateUserForm
    template_name = 'registration.html'
    success_url = reverse_lazy('user:login')

class UserLogin(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('hotel_app:index')

class UserLogout(LogoutView):
    next_page = reverse_lazy('user:login')

class UserProfileView(LoginRequiredMixin, View):
    template_name = 'user_profile.html'

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        p_form = UserProfileForm(instance=profile)
        reservation = (Reservation.objects.filter(user=request.user).select_related('hotel', 'room').order_by(
            Case(When(status='active', then=1), When(status='upcoming', then=2),
                        When(status='completed', then=3),When(status='canceled', then=4),
                        default=5, output_field=IntegerField() ), '-check_in'))

        return render(request, self.template_name, {'p_form': p_form, 'profile': profile, 'user': request.user, 'reservations': reservation})

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if p_form.is_valid():
            p_form.save()
            return redirect('user:profile')
        return render(request, self.template_name, {'p_form': p_form})
