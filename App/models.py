from django.db import models
from django.contrib.auth.models import User


# Modelo Usuario extendido para diferentes tipos de usuarios
class UserProfile(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('secretaria', 'Secretaria'),
        ('administrador', 'Administrador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

# Modelo Paciente
class Paciente(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='paciente_profile')
    dpi = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField(null=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    seguro_medico = models.CharField(max_length=50, blank=True, null=True)
    blood_type = models.CharField(max_length=3)
    conditions = models.TextField(blank=True, null=True)  # Padecimientos

    def __str__(self):
        return f"Paciente: {self.user_profile.user.username}"

# Modelo Especialidad
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre de la especialidad, debe ser única

    def __str__(self):
        return self.nombre


# Modelo Médico actualizado
class Medico(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='medico_profile')
    colegiado = models.CharField(max_length=20)  # Número de colegiado del médico
    dpi = models.CharField(max_length=15)  # DPI del médico
    telefono = models.CharField(max_length=15)  # Teléfono del médico
    direccion = models.TextField()  # Dirección del médico
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)  # Relación con Especialidad

    def __str__(self):
        return f"Dr. {self.user_profile.user.username} - {self.especialidad.nombre}"



# Modelo Secretaria actualizado
class Secretaria(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='secretaria_profile')
    dpi = models.CharField(max_length=15)  # DPI de la secretaria
    telefono = models.CharField(max_length=15)  # Teléfono de la secretaria
    direccion = models.TextField()  # Dirección de la secretaria

    def __str__(self):
        return f"Secretaria: {self.user_profile.user.username}"



from datetime import timedelta
from django.utils import timezone


#######modelo horario##########
from django.db import models
from django.conf import settings

class Horario(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    dia = models.DateField(help_text="Ingrese una fecha para la agenda")
    
    HORARIOS = (
        ("1", "06:00-06:30"),
        ("2", "06:30-07:00"),
        ("3", "07:00-07:30"),
        ("4", "07:30-08:00"),
        ("5", "08:00-08:30"),
        ("6", "08:30-09:00"),
        ("7", "09:00-09:30"),
        ("8", "09:30-10:00"),
        ("9", "10:00-10:30"),
        ("10", "10:30-11:00"),
        ("11", "11:00-11:30"),
        ("12", "11:30-12:00"),
        ("13", "12:00-12:30"),
        ("14", "12:30-13:00"),
        ("15", "13:00-13:30"),
        ("16", "13:30-14:00"),
        ("17", "14:00-14:30"),
        ("18", "14:30-15:00"),
        ("19", "15:00-15:30"),
        ("20", "15:30-16:00"),
        ("21", "16:00-16:30"),
        ("22", "16:30-17:00"),
        ("23", "17:00-17:30"),
        ("24", "17:30-18:00"),
    )
    
    horario = models.CharField(max_length=10, choices=HORARIOS)
    

    disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('medico', 'dia', 'horario')  # Asegura que no haya duplicados

    def __str__(self):
        return f'{self.dia.strftime("%b %d %Y")} - {self.get_horario_display()} - {self.medico}'




# Modelo Cita
class Cita(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, 
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada')
        ], 
        default='pendiente'
    )
    
    class Meta:
        unique_together = ('usuario', 'horario')  # Un usuario no puede tener dos citas en el mismo horario

    def __str__(self):
        return f'Cita para {self.usuario.username} - {self.horario}'


# Modelo Historial Clínico
class HistorialClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historiales_clinicos')
    fecha = models.DateField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historial clínico de {self.paciente} - {self.fecha}"
