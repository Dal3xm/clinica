# app/urls.py

from django.urls import path
from .views import loginView, home, exit, defaultView, UserListView, UserCreateView, UserUpdateView, UserDeleteView
from .views import (
    HistorialClinicoListView, HistorialClinicoDetailView, HistorialClinicoCreateView, HistorialClinicoUpdateView, 
    HistorialClinicoDeleteView, EditUserProfileView, UserProfileEditView, UserProfileDetailView,UserSelfUpdateView, PatientSignUpView,
    HorarioListView,HorarioUpdateView,HorarioDeleteView)

from .views import HorarioListView, HorarioMultipleCreateView, HorarioUpdateView, HorarioDeleteView, HorarioDetailView
from .views import CitaListView, CitaCreateView, CitaUpdateView, CitaDeleteView, CitaDetailView, PacienteHistorialClinicoListView, HorarioMedicoListView

urlpatterns = [
    path('', defaultView, name='defaultView'),
    path('home/', home, name='home'),
    path('logout/', exit, name='exit'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/new/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('signup/', PatientSignUpView.as_view(), name='patient_signup'),

    path('profile/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('users/<int:pk>/edit-profile/', UserProfileEditView.as_view(), name='user_profile_edit'), #listado admin
    path('profile/edit/', EditUserProfileView.as_view(), name='edit_user_profile'), #propio
    path('user/edit/', UserSelfUpdateView.as_view(), name='edit_user_self'),
    
    
    path('horarios/', HorarioListView.as_view(), name='horario_list'),
    path('horarios/nuevo/', HorarioMultipleCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/', HorarioDetailView.as_view(), name='horario_detail'),
    path('horarios/<int:pk>/editar/', HorarioUpdateView.as_view(), name='horario_edit'),
    path('horarios/<int:pk>/eliminar/', HorarioDeleteView.as_view(), name='horario_delete'),
    path('horarios/mis-horarios/', HorarioMedicoListView.as_view(), name='mis_horarios'),


    path('citas/', CitaListView.as_view(), name='cita_list'),
    path('citas/nueva/', CitaCreateView.as_view(), name='cita_create'),
    path('citas/<int:pk>/', CitaDetailView.as_view(), name='cita_detail'),
    path('citas/<int:pk>/editar/', CitaUpdateView.as_view(), name='cita_edit'),
    path('citas/<int:pk>/eliminar/', CitaDeleteView.as_view(), name='cita_delete'),

    # URLs para Historial Clinico
    path('historiales/', HistorialClinicoListView.as_view(), name='historial_list'),
    path('historiales/<int:pk>/', HistorialClinicoDetailView.as_view(), name='historial_detail'),
    path('historiales/nuevo/', HistorialClinicoCreateView.as_view(), name='historial_create'),
    path('historiales/editar/<int:pk>/', HistorialClinicoUpdateView.as_view(), name='historial_update'),
    path('historiales/eliminar/<int:pk>/', HistorialClinicoDeleteView.as_view(), name='historial_delete'),
    
    path('pacientes/<int:pk>/historiales/', PacienteHistorialClinicoListView.as_view(), name='paciente_historiales'),
    path('pacientes/<int:pk>/perfil/', UserProfileDetailView.as_view(), name='paciente_profile'),

]


