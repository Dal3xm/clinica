# Generated by Django 5.0.7 on 2024-08-23 06:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Especialidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dpi', models.CharField(max_length=15)),
                ('fecha_nacimiento', models.DateField(null=True)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=15)),
                ('seguro_medico', models.CharField(blank=True, max_length=50, null=True)),
                ('blood_type', models.CharField(max_length=3)),
                ('conditions', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colegiado', models.CharField(max_length=20)),
                ('dpi', models.CharField(max_length=15)),
                ('telefono', models.CharField(max_length=15)),
                ('direccion', models.TextField()),
                ('especialidad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='App.especialidad')),
            ],
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.DateField(help_text='Ingrese una fecha para la agenda')),
                ('horario', models.CharField(choices=[('1', '06:00-06:30'), ('2', '06:30-07:00'), ('3', '07:00-07:30'), ('4', '07:30-08:00'), ('5', '08:00-08:30'), ('6', '08:30-09:00'), ('7', '09:00-09:30'), ('8', '09:30-10:00'), ('9', '10:00-10:30'), ('10', '10:30-11:00'), ('11', '11:00-11:30'), ('12', '11:30-12:00'), ('13', '12:00-12:30'), ('14', '12:30-13:00'), ('15', '13:00-13:30'), ('16', '13:30-14:00'), ('17', '14:00-14:30'), ('18', '14:30-15:00'), ('19', '15:00-15:30'), ('20', '15:30-16:00'), ('21', '16:00-16:30'), ('22', '16:30-17:00'), ('23', '17:00-17:30'), ('24', '17:30-18:00')], max_length=10)),
                ('disponible', models.BooleanField(default=True)),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='App.medico')),
            ],
            options={
                'unique_together': {('medico', 'dia', 'horario')},
            },
        ),
        migrations.CreateModel(
            name='HistorialClinico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('diagnostico', models.TextField()),
                ('tratamiento', models.TextField()),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiales_clinicos', to='App.paciente')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_usuario', models.CharField(choices=[('paciente', 'Paciente'), ('medico', 'Médico'), ('secretaria', 'Secretaria'), ('administrador', 'Administrador')], max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Secretaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dpi', models.CharField(max_length=15)),
                ('telefono', models.CharField(max_length=15)),
                ('direccion', models.TextField()),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='secretaria_profile', to='App.userprofile')),
            ],
        ),
        migrations.AddField(
            model_name='paciente',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paciente_profile', to='App.userprofile'),
        ),
        migrations.AddField(
            model_name='medico',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='medico_profile', to='App.userprofile'),
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('horario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.horario')),
            ],
            options={
                'unique_together': {('usuario', 'horario')},
            },
        ),
    ]
