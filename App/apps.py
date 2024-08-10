from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'


# app/apps.py

from django.apps import AppConfig

class AppNameConfig(AppConfig):
    name = 'App'

    def ready(self):
        import App.signals
