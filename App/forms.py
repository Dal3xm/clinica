from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from .models import UserProfile, Paciente, Medico, Secretaria, Cita, HistorialClinico


from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Paciente, Medico, Secretaria, Horario


######################formulario registro para pacientes############################

class PatientSignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirma tu contraseña', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Tu nombre', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Tu apellido', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Tu correo electrónico', 'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



#############formulario de usuarios############################

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña', 'class': 'form-control'})
    )
    tipo_usuario = forms.ChoiceField(
        choices=UserProfile.TIPO_USUARIO_CHOICES, 
        label="Tipo de usuario", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        # Guardar el usuario
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
            # Crear o actualizar el perfil del usuario
            tipo_usuario = self.cleaned_data['tipo_usuario']
            user_profile, created = UserProfile.objects.update_or_create(
                user=user, 
                defaults={'tipo_usuario': tipo_usuario}
            )

            # Crear el perfil específico según el tipo de usuario
            if tipo_usuario == 'paciente':
                Paciente.objects.create(user_profile=user_profile)
            elif tipo_usuario == 'medico':
                Medico.objects.create(user_profile=user_profile)
            elif tipo_usuario == 'secretaria':
                Secretaria.objects.create(user_profile=user_profile)

        return user


#formulario de actualizacion de usuario

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class': 'form-control'}), 
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña', 'class': 'form-control'}), 
        required=False
    )
    tipo_usuario = forms.ChoiceField(
        choices=UserProfile.TIPO_USUARIO_CHOICES, 
        label="Tipo de usuario", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 or password2:  # Solo validamos si se han ingresado contraseñas
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Actualizar o crear el perfil de usuario
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            # Actualiza el tipo de usuario si es necesario
            user_profile.tipo_usuario = self.cleaned_data['tipo_usuario']
            user_profile.save()
        return user


# Formularios específicos para cada tipo de usuario podrían extenderse de este formulario base, similar a como se hace con `UserCreationForm`.

from django import forms
from .models import Paciente, Medico, Secretaria, Cita, HistorialClinico

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dpi', 'fecha_nacimiento', 'direccion', 'telefono', 'seguro_medico', 'blood_type', 'conditions']
        widgets = {
            'dpi': forms.TextInput(attrs={'placeholder': 'DPI', 'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'placeholder': 'Dirección', 'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'seguro_medico': forms.TextInput(attrs={'placeholder': 'Seguro Médico', 'class': 'form-control'}),
            'blood_type': forms.TextInput(attrs={'placeholder': 'Tipo de Sangre', 'class': 'form-control'}),
            'conditions': forms.Textarea(attrs={'placeholder': 'Padecimientos o Condiciones', 'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


###########formulario admin###############
class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['colegiado', 'dpi', 'telefono', 'direccion', 'especialidad']
        widgets = {
            'colegiado': forms.TextInput(attrs={'placeholder': 'Número de Colegiado', 'class': 'form-control'}),
            'dpi': forms.TextInput(attrs={'placeholder': 'DPI', 'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'placeholder': 'Dirección', 'class': 'form-control', 'rows': 3}),
            'especialidad': forms.Select(attrs={'class': 'form-control'}),  # Menú desplegable para Especialidad
        }

##############formulario propio usuario###########
class MedicoFormSelf(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['colegiado', 'dpi', 'telefono', 'direccion']
        widgets = {
            'colegiado': forms.TextInput(attrs={'placeholder': 'Número de Colegiado', 'class': 'form-control'}),
            'dpi': forms.TextInput(attrs={'placeholder': 'DPI', 'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'placeholder': 'Dirección', 'class': 'form-control', 'rows': 3}),
        }



class SecretariaForm(forms.ModelForm):
    class Meta:
        model = Secretaria
        fields = ['dpi', 'telefono', 'direccion']
        widgets = {
            'dpi': forms.TextInput(attrs={'placeholder': 'DPI', 'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'placeholder': 'Dirección', 'class': 'form-control', 'rows': 3}),
        }




# Formulario para Historial Clinico
class HistorialClinicoForm(forms.ModelForm):
    class Meta:
        model = HistorialClinico
        fields = ['paciente', 'fecha', 'diagnostico', 'tratamiento', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

###################formulario para que usario edite sus propios datos######################
class UserSelfUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva Contraseña', 'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


###############creacion de horario############################



from django import forms
from .models import Horario

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['medico', 'dia', 'horario']
        
        widgets = {
            'medico': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horario': forms.Select(attrs={'class': 'form-control'}),
        }


#formulario citas

from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['usuario', 'horario', 'estado']  # Mantén el campo usuario

        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'horario': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Recibir el usuario actual desde la vista
        super(CitaForm, self).__init__(*args, **kwargs)

        if user and user.profile.tipo_usuario == 'paciente':
            # Si el usuario es paciente, ocultar el campo usuario
            self.fields.pop('usuario')
            self.fields.pop('estado')
        else:
            # Si el usuario es admin o secretaria, mostrar todos los usuarios en el campo usuario
            self.fields['usuario'].queryset = User.objects.filter(profile__tipo_usuario='paciente')