# app/urls.py

from django.urls import path
from .views import loginView, home, exit, defaultView, UserListView, UserCreateView, UserUpdateView, UserDeleteView, PatientSignUpView,PatientProfileDetailView,PatientProfileUpdateView
from .views import HorarioListView, HorarioCreateView

urlpatterns = [
    path('', defaultView, name='defaultView'),
    path('home/', home, name='home'),
    path('logout/', exit, name='exit'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/new/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('signup/', PatientSignUpView.as_view(), name='patient_signup'),  # Nueva ruta para registro de pacientes
    path('profile/', PatientProfileDetailView.as_view(), name='patient_profile_detail'),
    path('profile/edit/', PatientProfileUpdateView.as_view(), name='patient_profile_edit'),
    path('horarios/', HorarioListView.as_view(), name='horario_list'),
    path('horarios/nuevo/', HorarioCreateView.as_view(), name='horario_create'),
]
