import re
from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from .models import PatientProfile
from .models import Horario


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        help_text='La contraseña debe tener al menos 8 caracteres e incluir letras y números.'
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label='Grupo',
        widget=forms.Select(attrs={'placeholder': 'Grupo'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
        help_texts = {
            'username': 'Requerido. Solo letras y dígitos.',
        }
        error_messages = {
            'username': {
                'required': 'Este campo es obligatorio',
                'invalid': 'Introduce un nombre de usuario válido. Solo puede contener letras y números.',
            },
            'email': {
                'invalid': 'Introduce una dirección de correo electrónico válida',
            },
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match('^[a-zA-Z0-9]*$', username):
            raise ValidationError('El nombre de usuario solo puede contener letras y números.')
        return username.upper()

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match('^[a-zA-Z]*$', first_name):
            raise ValidationError('El nombre solo puede contener letras.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match('^[a-zA-Z]*$', last_name):
            raise ValidationError('El apellido solo puede contener letras.')
        return last_name

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Las contraseñas no coinciden.')

            if len(password1) < 8:
                raise ValidationError('La contraseña debe tener al menos 8 caracteres.')

            if not re.search('[a-zA-Z]', password1) or not re.search('[0-9]', password1):
                raise ValidationError('La contraseña debe incluir letras y números.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.username.upper()  # Convertir el nombre de usuario a mayúsculas
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.groups.add(self.cleaned_data['group'])
        return user


class PatientSignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        help_text='La contraseña debe tener al menos 8 caracteres e incluir letras y números.'
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            group = Group.objects.get(name='pacientes')  # Asegúrate de que el grupo "pacientes" existe
            user.groups.add(group)
        return user


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['dpi', 'nit', 'address', 'phone', 'mobile', 'birth_date', 'blood_type', 'conditions']
        widgets = {
            'dpi': forms.TextInput(attrs={'placeholder': 'DPI', 'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'placeholder': 'NIT', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dirección', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Celular', 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'placeholder': 'Fecha de Nacimiento', 'class': 'form-control', 'type': 'date'}),
            'blood_type': forms.TextInput(attrs={'placeholder': 'Tipo de Sangre', 'class': 'form-control'}),
            'conditions': forms.TextInput(attrs={'placeholder': 'Padecimientos', 'class': 'form-control'}),
        }



class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['medico', 'dia', 'hora_inicio', 'hora_fin']
