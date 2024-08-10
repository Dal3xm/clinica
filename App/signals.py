# app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PatientProfile

@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.groups.filter(name='Pacientes').exists():
        PatientProfile.objects.create(user=instance)
