from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.contrib.auth.models import User

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    dpi = models.CharField(max_length=15)
    nit = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15)
    birth_date = models.DateField(blank=True, null=True)
    blood_type = models.CharField(max_length=3)
    conditions = models.TextField(blank=True, null=True)  # Padecimientos

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Horario(models.Model):
    DIAS_CHOICES = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miercoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sabado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    medico = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Medicos'})
    dia = models.CharField(max_length=10, choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.medico.username} - {self.dia} {self.hora_inicio} - {self.hora_fin}"