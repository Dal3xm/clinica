# app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import UserCreationForm, PatientProfileForm
import json
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PatientProfile
from .models import Horario
from .forms import HorarioForm
from .forms import PatientSignUpForm



#horario
class HorarioCreateView(UserPassesTestMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'horario_form.html'
    success_url = reverse_lazy('horario_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()

class HorarioListView(UserPassesTestMixin, ListView):
    model = Horario
    template_name = 'horario_list.html'
    context_object_name = 'horarios'

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()



#registro de pacientes
class PatientSignUpView(CreateView):
    model = User
    form_class = PatientSignUpForm
    template_name = 'registration/patient_signup.html'
    success_url = reverse_lazy('login')  # Redirige al login después de registrarse


# Vistas basadas en clases para CRUD de usuarios
class UserListView(UserPassesTestMixin,ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir los grupos al contexto
        users_with_groups = []
        for user in context['users']:
            user_groups = user.groups.all()
            users_with_groups.append((user, user_groups))
        context['users_with_groups'] = users_with_groups
        return context
    
    # Verifica si el usuario pertenece al grupo "Administradores"
    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()

    # Si no pertenece al grupo, redirige a otra página
    def handle_no_permission(self):
            return redirect('home')  # Redirige a la vista que desees

    
class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()

    def handle_no_permission(self):
            return redirect('home')  

class UserUpdateView(UpdateView):
    model = User
    form_class = UserCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()

    def handle_no_permission(self):
            return redirect('home')  


class UserDeleteView(DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()

    def handle_no_permission(self):
            return redirect('home')  
    

# app/views.py


from django.shortcuts import get_object_or_404

class PatientProfileDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'patient_profile_detail.html'

    def get_object(self):
        user = self.request.user
        # Intentar obtener el perfil, o crearlo si no existe
        try:
            return user.patient_profile
        except PatientProfile.DoesNotExist:
            # Crear el perfil si no existe
            return PatientProfile.objects.create(user=user)

# app/views.py

class PatientProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = PatientProfile
    form_class = PatientProfileForm
    template_name = 'patient_profile_form.html'
    success_url = reverse_lazy('patient_profile_detail')

    def get_object(self):
        # Devolver el perfil del paciente relacionado con el usuario logueado
        return self.request.user.patient_profile




# Otras vistas existentes
def defaultView(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def loginView(request):
    return render(request, 'login.html')

@login_required
@login_required
def home(request):
    is_admin = request.user.groups.filter(name='Administradores').exists()
    return render(request, 'home.html', {'is_admin': is_admin})

def exit(request):
    logout(request)
    return redirect('login')

def is_superuser(user):
    return user.is_superuser


