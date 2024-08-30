# app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserCreationForm, UserUpdateForm
from .models import Paciente, Medico, Secretaria, Cita, HistorialClinico, UserProfile
from .forms import PacienteForm, MedicoForm, SecretariaForm, HistorialClinicoForm, UserSelfUpdateForm, MedicoFormSelf, PatientSignUpForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


############registro de pacientes##########################
class PatientSignUpView(CreateView):
    model = User
    form_class = PatientSignUpForm
    template_name = 'registration/signup_patient.html'  # Puedes crear una plantilla personalizada para el registro de pacientes
    success_url = reverse_lazy('home')  # Redirige donde quieras después del registro

    def form_valid(self, form):
        # Guardar el usuario
        user = form.save()
        # Crear automáticamente el perfil del paciente
        user_profile = UserProfile.objects.create(user=user, tipo_usuario='paciente')
        # Crear el perfil del paciente asociado
        Paciente.objects.create(user_profile=user_profile)
        
        return super().form_valid(form)


###############lista de usuarios##########################

class UserListView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Filtra los usuarios que no son superusuarios
        return User.objects.filter(is_superuser=False)

    def test_func(self):
        # Verifica si el usuario es un administrador basado en UserProfile
        try:
            return self.request.user.profile.tipo_usuario == 'administrador'
        except UserProfile.DoesNotExist:
            return False  # Si no tiene UserProfile, no es un administrador

    def handle_no_permission(self):
        return redirect('home')
    
    

# Vista para crear usuarios (solo administradores)
class UserCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        # Verifica si el usuario es un administrador basado en UserProfile
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')

class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Prellenar tipo_usuario
        if hasattr(self.object, 'profile'):
            form.fields['tipo_usuario'].initial = self.object.profile.tipo_usuario
        return form

########### Vista para eliminar usuarios (solo administradores)#############
class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        # Verifica si el usuario es un administrador basado en UserProfile
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')
    
########################administrador edita perfil######################################
class UserProfileEditView(UserPassesTestMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def get_object(self):
        # Obtiene el perfil del usuario basado en el ID proporcionado en la URL
        user_profile = get_object_or_404(UserProfile, user__pk=self.kwargs['pk'])
        return user_profile

    def get_form_class(self):
        user_profile = self.get_object()

        # Selecciona el formulario correspondiente basado en el tipo de usuario
        if user_profile.tipo_usuario == 'paciente':
            return PacienteForm
        elif user_profile.tipo_usuario == 'medico':
            return MedicoForm
        elif user_profile.tipo_usuario == 'secretaria':
            return SecretariaForm
        else:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_instance()
        return kwargs

    def get_instance(self):
        user_profile = self.get_object()
        if user_profile.tipo_usuario == 'paciente':
            return get_object_or_404(Paciente, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'medico':
            return get_object_or_404(Medico, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'secretaria':
            return get_object_or_404(Secretaria, user_profile=user_profile)
        else:
            return None

    def handle_no_permission(self):
        return redirect('home')



####################cada usuario edita sus datos############################
from django.urls import reverse

class UserSelfUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSelfUpdateForm
    template_name = 'edit_user.html'

    def get_success_url(self):
        # Redirige al perfil del usuario actual
        return reverse('user_profile_detail')

    def get_object(self, queryset=None):
        return self.request.user




##########################cada usuario edita su perfil#############################
class EditUserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    success_url = reverse_lazy('profile')  # Redirige a la vista de perfil o donde prefieras

    def get_object(self):
        # Obtiene el perfil de usuario basado en el usuario autenticado
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return user_profile

    def get_form_class(self):
        user_profile = self.get_object()

        # Selecciona el formulario correspondiente basado en el tipo de usuario
        if user_profile.tipo_usuario == 'paciente':
            return PacienteForm
        elif user_profile.tipo_usuario == 'medico':
            return MedicoFormSelf
        elif user_profile.tipo_usuario == 'secretaria':
            return SecretariaForm
        else:
            return None  # Retorna None si no hay un tipo de usuario válido

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Añade la instancia correcta del modelo relacionado al formulario
        kwargs['instance'] = self.get_instance()
        return kwargs

    def get_instance(self):
        # Obtiene la instancia correcta del modelo relacionado basado en el tipo de usuario
        user_profile = self.get_object()

        if user_profile.tipo_usuario == 'paciente':
            return get_object_or_404(Paciente, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'medico':
            return get_object_or_404(Medico, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'secretaria':
            return get_object_or_404(Secretaria, user_profile=user_profile)
        else:
            return None

    def dispatch(self, request, *args, **kwargs):
        # Redirige a la página de inicio si el tipo de usuario no está soportado
        if not self.get_form_class():
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)






##############vista perfil################

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import UserProfile, Paciente, Medico, Secretaria
from django.contrib.auth.mixins import LoginRequiredMixin

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        # Verifica si hay un 'pk' en la URL, lo usa para obtener el perfil de ese usuario
        if 'pk' in self.kwargs:
            user_profile = get_object_or_404(UserProfile, pk=self.kwargs['pk'])
        else:
            # Si no hay 'pk', usa el perfil del usuario autenticado
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return user_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()

        # Añade los datos específicos del perfil basado en el tipo de usuario
        if user_profile.tipo_usuario == 'paciente':
            context['profile_data'] = get_object_or_404(Paciente, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'medico':
            context['profile_data'] = get_object_or_404(Medico, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'secretaria':
            context['profile_data'] = get_object_or_404(Secretaria, user_profile=user_profile)

        return context






# Vistas para Historial Clinico
class HistorialClinicoListView(ListView):
    model = HistorialClinico
    template_name = 'historial_list.html'
    context_object_name = 'historiales_clinicos'

class HistorialClinicoDetailView(DetailView):
    model = HistorialClinico
    template_name = 'historial_detail.html'
    context_object_name = 'historial_clinico'

class HistorialClinicoCreateView(CreateView):
    model = HistorialClinico
    form_class = HistorialClinicoForm
    template_name = 'historial_form.html'
    success_url = reverse_lazy('historial_list')

class HistorialClinicoUpdateView(UpdateView):
    model = HistorialClinico
    form_class = HistorialClinicoForm
    template_name = 'historial_form.html'
    success_url = reverse_lazy('historial_list')

class HistorialClinicoDeleteView(DeleteView):
    model = HistorialClinico
    template_name = 'historial_confirm_delete.html'
    success_url = reverse_lazy('historial_list')



class PacienteHistorialClinicoListView(ListView):
    model = HistorialClinico
    template_name = 'paciente_historiales.html'
    context_object_name = 'historiales_clinicos'

    def get_queryset(self):
        # Obtener el perfil del usuario a través del 'pk' en la URL
        user_profile = get_object_or_404(UserProfile, pk=self.kwargs.get('pk'))
        
        # Verificar si el perfil es de un paciente
        if hasattr(user_profile, 'paciente_profile'):
            paciente = user_profile.paciente_profile
            return HistorialClinico.objects.filter(paciente=paciente)
        else:
            # Si no es un paciente, devolver un queryset vacío
            return HistorialClinico.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = get_object_or_404(UserProfile, pk=self.kwargs.get('pk'))
        
        # Agregar el paciente al contexto si es un paciente
        if hasattr(user_profile, 'paciente_profile'):
            context['paciente'] = user_profile.paciente_profile
        else:
            context['paciente'] = None  # No es un paciente
        
        return context
    
#############vista horarios############

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Horario
from .forms import HorarioForm  # Asegúrate de importar el formulario personalizado

# Listar los horarios
class HorarioListView(ListView):
    model = Horario
    template_name = 'horario_list.html'
    context_object_name = 'horarios'

# Crear un nuevo horario
class HorarioCreateView(CreateView):
    model = Horario
    form_class = HorarioForm  # Usamos el formulario personalizado
    template_name = 'horario_form.html'
    success_url = reverse_lazy('horario_list')

# Actualizar un horario existente
class HorarioUpdateView(UpdateView):
    model = Horario
    form_class = HorarioForm  # Usamos el formulario personalizado
    template_name = 'horario_form.html'
    success_url = reverse_lazy('horario_list')

# Eliminar un horario
class HorarioDeleteView(DeleteView):
    model = Horario
    template_name = 'horario_confirm_delete.html'
    success_url = reverse_lazy('horario_list')

# Ver detalles de un horario específico
class HorarioDetailView(DetailView):
    model = Horario
    template_name = 'horario_detail.html'
    context_object_name = 'horario'




#########vistas citas##################################

from .models import Cita
from .forms import CitaForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Crear una nueva cita
class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'cita_form.html'
    success_url = reverse_lazy('cita_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasamos el usuario actual al formulario
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.profile.tipo_usuario == 'paciente':
            # Asignar automáticamente el usuario autenticado si es paciente
            form.instance.usuario = self.request.user
        return super().form_valid(form)

# Actualizar una cita existente
class CitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'cita_form.html'
    success_url = reverse_lazy('cita_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasamos el usuario actual al formulario
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        # Admins y secretarias pueden editar cualquier cita, pacientes solo las suyas
        if self.request.user.profile.tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.all()
        return Cita.objects.filter(usuario=self.request.user)

# Eliminar una cita
class CitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = 'cita_confirm_delete.html'
    success_url = reverse_lazy('cita_list')

    def get_queryset(self):
        # Admins y secretarias pueden eliminar cualquier cita, pacientes solo las suyas
        if self.request.user.profile.tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.all()
        return Cita.objects.filter(usuario=self.request.user)

# Ver detalles de una cita específica
class CitaDetailView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = 'cita_detail.html'
    context_object_name = 'cita'

    def get_queryset(self):
        # Admins y secretarias pueden ver cualquier cita, pacientes solo las suyas
        if self.request.user.profile.tipo_usuario in ['administrador', 'secretaria','medico']:
            return Cita.objects.all()
        return Cita.objects.filter(usuario=self.request.user)

# Listar las citas del usuario autenticado
class CitaListView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = 'cita_list.html'
    context_object_name = 'citas'

    def get_queryset(self):
        user_profile = self.request.user.profile
        tipo_usuario = user_profile.tipo_usuario

        # Admins y secretarias pueden ver todas las citas
        if tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.all()
        
        # Pacientes solo pueden ver sus propias citas
        elif tipo_usuario == 'paciente':
            return Cita.objects.filter(usuario=self.request.user)
        
        # Médicos pueden ver las citas de sus horarios
        elif tipo_usuario == 'medico':
            # Filtrar citas basadas en los horarios asignados al médico
            return Cita.objects.filter(horario__medico=user_profile.medico_profile)
        
        # Devolver un queryset vacío por defecto
        return Cita.objects.none()


# ####################Otras vistas existentes###########
def defaultView(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def loginView(request):
    return render(request, 'login.html')


@login_required
def home(request):
    is_admin = request.user.groups.filter(name='Administradores').exists()
    return render(request, 'home.html', {'is_admin': is_admin})

def exit(request):
    logout(request)
    return redirect('login')

def is_superuser(user):
    return user.is_superuser
