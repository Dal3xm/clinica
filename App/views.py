from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .forms import HorarioFilterForm, UserCreationForm, UserUpdateForm, PacienteForm, MedicoForm, SecretariaForm, HistorialClinicoForm, UserSelfUpdateForm, MedicoFormSelf, PatientSignUpForm
from .models import Paciente, Medico, Secretaria, Cita, HistorialClinico, UserProfile
from django.shortcuts import get_object_or_404


# Registro de pacientes
class PatientSignUpView(CreateView):
    model = User
    form_class = PatientSignUpForm
    template_name = 'registration/signup_patient.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        user_profile = UserProfile.objects.create(user=user, tipo_usuario='paciente')
        Paciente.objects.create(user_profile=user_profile)
        return super().form_valid(form)


# Lista de usuarios (solo para administradores)
class UserListView(ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Obtener el tipo de usuario del filtro de la URL
        tipo_usuario = self.request.GET.get('tipo_usuario')

        # Filtrar solo los usuarios que no son superusuarios
        queryset = User.objects.filter(is_superuser=False)

        if tipo_usuario:
            # Filtrar por el tipo de usuario si se proporciona un filtro
            queryset = queryset.filter(profile__tipo_usuario=tipo_usuario)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar el valor actual del filtro al contexto para mantener el filtro en el template
        context['selected_filter'] = self.request.GET.get('tipo_usuario', '')
        return context

# Crear usuario (solo para administradores)
class UserCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')


# Actualizar usuario (solo para administradores)
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
        if hasattr(self.object, 'profile'):
            form.fields['tipo_usuario'].initial = self.object.profile.tipo_usuario
        return form


# Eliminar usuario (solo para administradores)
class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')


# Administrador edita perfil de usuario
class UserProfileEditView(UserPassesTestMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def get_object(self):
        user_profile = get_object_or_404(UserProfile, user__pk=self.kwargs['pk'])
        return user_profile

    def get_form_class(self):
        user_profile = self.get_object()
        if user_profile.tipo_usuario == 'paciente':
            return PacienteForm
        elif user_profile.tipo_usuario == 'medico':
            return MedicoForm
        elif user_profile.tipo_usuario == 'secretaria':
            return SecretariaForm
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
        return None

    def handle_no_permission(self):
        return redirect('home')


# Cada usuario edita su propio usuario
class UserSelfUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSelfUpdateForm
    template_name = 'edit_user.html'

    def get_success_url(self):
        return reverse('user_profile_detail')

    def get_object(self, queryset=None):
        return self.request.user


# Cada usuario edita su propio perfil
class EditUserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'user_profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return user_profile

    def get_form_class(self):
        user_profile = self.get_object()
        if user_profile.tipo_usuario == 'paciente':
            return PacienteForm
        elif user_profile.tipo_usuario == 'medico':
            return MedicoFormSelf
        elif user_profile.tipo_usuario == 'secretaria':
            return SecretariaForm
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
        return None

    def dispatch(self, request, *args, **kwargs):
        if not self.get_form_class():
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


# Vista de perfil de usuario (detalles)
class UserProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_profile_detail.html'
    context_object_name = 'profile'

    def get_template_names(self):
        if self.request.user.profile.tipo_usuario == 'medico' and 'pk' in self.kwargs:
            return ['paciente_profile_for_medico.html']
        return [self.template_name]

    def get_object(self):
        if 'pk' in self.kwargs:
            user = get_object_or_404(User, pk=self.kwargs['pk'])
        else:
            user = self.request.user
        return get_object_or_404(UserProfile, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        if user_profile.tipo_usuario == 'paciente':
            context['profile_data'] = get_object_or_404(Paciente, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'medico':
            context['profile_data'] = get_object_or_404(Medico, user_profile=user_profile)
        elif user_profile.tipo_usuario == 'secretaria':
            context['profile_data'] = get_object_or_404(Secretaria, user_profile=user_profile)
        return context



from django.http import HttpResponseForbidden

# Vistas para Historial Clinico
# Lista de historiales clínicos
class HistorialClinicoListView(ListView):
    model = HistorialClinico
    template_name = 'historial_list.html'
    context_object_name = 'historiales_clinicos'

    def get_queryset(self):
        user_profile = self.request.user.profile
        if user_profile.tipo_usuario == 'medico':
            return HistorialClinico.objects.all()
        elif user_profile.tipo_usuario == 'paciente':
            return HistorialClinico.objects.filter(paciente__user_profile=user_profile)
        elif user_profile.tipo_usuario == 'administrador':
            return HistorialClinico.objects.all()
        return HistorialClinico.objects.none()


# Detalles de un historial clínico
class HistorialClinicoDetailView(DetailView):
    model = HistorialClinico
    template_name = 'historial_detail.html'
    context_object_name = 'historial_clinico'


# Crear historial clínico (solo médicos)
class HistorialClinicoCreateView(LoginRequiredMixin, CreateView):
    model = HistorialClinico
    form_class = HistorialClinicoForm
    template_name = 'historial_form.html'
    success_url = reverse_lazy('historial_list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.profile.tipo_usuario != 'medico':
            return HttpResponseForbidden("Solo los médicos pueden crear historiales clínicos.")
        return super().dispatch(request, *args, **kwargs)


# Editar historial clínico (solo médicos)
class HistorialClinicoUpdateView(LoginRequiredMixin, UpdateView):
    model = HistorialClinico
    form_class = HistorialClinicoForm
    template_name = 'historial_form.html'
    success_url = reverse_lazy('historial_list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.profile.tipo_usuario != 'medico':
            return HttpResponseForbidden("Solo los médicos pueden editar historiales clínicos.")
        return super().dispatch(request, *args, **kwargs)


# Eliminar historial clínico (solo administradores)
class HistorialClinicoDeleteView(UserPassesTestMixin, DeleteView):
    model = HistorialClinico
    template_name = 'historial_confirm_delete.html'
    success_url = reverse_lazy('historial_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')




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

from .models import Horario, Medico
from django import forms
from django.views.generic import ListView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class HorarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Horario
    template_name = 'horario_list.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        medico_id = self.request.GET.get('medico')
        dia = self.request.GET.get('dia')

        if medico_id and dia:
            # Filtrar los horarios por médico y fecha
            return Horario.objects.filter(medico__id=medico_id, dia=dia)
        return Horario.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = HorarioFilterForm(self.request.GET or None)

        medico_id = self.request.GET.get('medico')
        dia = self.request.GET.get('dia')

        if medico_id and dia:
            # Si se ha enviado el filtro, obtener los horarios ocupados
            horarios_filtrados = self.get_queryset()
            horarios_dict = {horario.horario: horario for horario in horarios_filtrados}

            context['all_horarios'] = Horario.HORARIOS  # Todos los horarios posibles
            context['horarios_filtrados'] = horarios_dict  # Diccionario de horarios ya ocupados por clave
            context['medico_id'] = medico_id  # Para utilizar en el formulario de crear horarios
            context['dia'] = dia  # Para el formulario de crear horarios

        return context

    def test_func(self):
        return self.request.user.profile.tipo_usuario in ['administrador']

    def handle_no_permission(self):
        return redirect('home')




########################crear horarios############################

# Crear un nuevo horario (solo administradores)
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Horario
from .forms import HorarioMultipleForm
from .models import Medico
class HorarioMultipleCreateView(UserPassesTestMixin, CreateView):
    form_class = HorarioMultipleForm
    template_name = 'horario_form.html'
    success_url = reverse_lazy('horario_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = self.request.GET.get('medico')
        dia = self.request.GET.get('dia')

        if medico_id and dia:
            medico = Medico.objects.get(id=medico_id)
            horarios_existentes = Horario.objects.filter(medico=medico, dia=dia)

            # Crear una lista de los horarios que tienen citas asociadas
            horarios_bloqueados = [horario.horario for horario in horarios_existentes if Cita.objects.filter(horario=horario).exists()]

            context['horarios_bloqueados'] = horarios_bloqueados  # Pasar los horarios bloqueados al contexto

        return context

    def post(self, request, *args, **kwargs):
        medico_id = request.POST.get('medico')
        dia = request.POST.get('dia')
        horarios_seleccionados = request.POST.getlist('horarios')

        if medico_id and dia:
            medico = Medico.objects.get(id=medico_id)
            horarios_existentes = Horario.objects.filter(medico=medico, dia=dia)
            errors = False

            # Crear nuevos horarios si no existen
            for horario in horarios_seleccionados:
                if not horarios_existentes.filter(horario=horario).exists():
                    Horario.objects.create(medico=medico, dia=dia, horario=horario, disponible=True)

            # Eliminar los horarios desmarcados, solo si no tienen citas asociadas
            for horario in horarios_existentes:
                if horario.horario not in horarios_seleccionados:
                    # Verificar si el horario tiene citas asociadas
                    if Cita.objects.filter(horario=horario).exists():
                        messages.error(self.request, f'No se puede eliminar el horario {horario.get_horario_display()} porque ya tiene una cita agendada.')
                        errors = True
                    else:
                        horario.delete()

            if errors:
                # Si hubo errores, volver a renderizar el formulario con los mensajes
                return self.get(request, *args, **kwargs)

            messages.success(self.request, 'Horarios actualizados correctamente para el médico.')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Faltan datos para actualizar los horarios.')
            return self.get(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')

############vista de horario para medicos########################################

from .models import Horario, Medico
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class HorarioMedicoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Horario
    template_name = 'horario_list_medico.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        # Filtrar los horarios por el médico autenticado y la fecha seleccionada
        medico = self.request.user.profile.medico_profile
        dia = self.request.GET.get('dia')

        if dia:
            # Mostrar solo los horarios del médico autenticado en la fecha seleccionada
            return Horario.objects.filter(medico=medico, dia=dia)
        return Horario.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = HorarioFilterForm(self.request.GET or None)

        dia = self.request.GET.get('dia')

        if dia:
            horarios_filtrados = self.get_queryset()
            horarios_dict = {horario.horario: horario for horario in horarios_filtrados}

            context['all_horarios'] = Horario.HORARIOS  # Todos los horarios posibles
            context['horarios_filtrados'] = horarios_dict  # Diccionario de horarios ya ocupados por clave
            context['dia'] = dia

        return context

    def test_func(self):
        # Solo los médicos pueden acceder a esta vista
        return self.request.user.profile.tipo_usuario == 'medico'

    def handle_no_permission(self):
        return redirect('home')


# Eliminar un horario (solo administradores)
class HorarioDeleteView(UserPassesTestMixin, DeleteView):
    model = Horario
    template_name = 'horario_confirm_delete.html'
    success_url = reverse_lazy('horario_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')


# Ver detalles de un horario específico
class HorarioDetailView(LoginRequiredMixin, DetailView):
    model = Horario
    template_name = 'horario_detail.html'
    context_object_name = 'horario'


# Actualizar un horario existente (solo administradores)
class HorarioUpdateView(UserPassesTestMixin, UpdateView):
    model = Horario
    form_class = HorarioMultipleForm
    template_name = 'horario_form.html'
    success_url = reverse_lazy('horario_list')

    def test_func(self):
        return self.request.user.profile.tipo_usuario == 'administrador'

    def handle_no_permission(self):
        return redirect('home')


#########vistas citas##################################

from .models import Cita
from .forms import CitaForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Cita

# Crear una nueva cita (pacientes, médicos, secretarias)
# Crear una nueva cita (pacientes, médicos, secretarias)
class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'cita_form.html'
    success_url = reverse_lazy('cita_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.profile.tipo_usuario == 'paciente':
            form.instance.usuario = self.request.user
        return super().form_valid(form)




# Actualizar una cita existente (administradores, secretarias)
class CitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'cita_form.html'
    success_url = reverse_lazy('cita_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        if self.request.user.profile.tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.all()
        return Cita.objects.filter(usuario=self.request.user)


# Eliminar una cita (administradores, secretarias)
class CitaDeleteView(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = 'cita_confirm_delete.html'
    success_url = reverse_lazy('cita_list')

    def get_queryset(self):
        if self.request.user.profile.tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.all()
        return Cita.objects.filter(usuario=self.request.user)


# Ver detalles de una cita específica (todos los roles)
class CitaDetailView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = 'cita_detail.html'
    context_object_name = 'cita'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cita = self.get_object()
        paciente_profile = get_object_or_404(Paciente, user_profile__user=cita.usuario)
        historiales_clinicos = HistorialClinico.objects.filter(paciente=paciente_profile)
        context['paciente'] = paciente_profile
        context['historiales_clinicos'] = historiales_clinicos
        return context


# Listar las citas del usuario autenticado (todos los roles)
from django.utils import timezone
class CitaListView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = 'cita_list.html'
    context_object_name = 'citas'

    def get_queryset(self):
        user_profile = self.request.user.profile
        today = timezone.now().date()

        # Filtrar citas basadas en el tipo de usuario
        if user_profile.tipo_usuario in ['administrador', 'secretaria']:
            return Cita.objects.filter(horario__dia__gte=today)
        elif user_profile.tipo_usuario == 'paciente':
            return Cita.objects.filter(usuario=self.request.user, horario__dia__gte=today)
        elif user_profile.tipo_usuario == 'medico':
            return Cita.objects.filter(horario__medico=user_profile.medico_profile, horario__dia__gte=today)
        
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
