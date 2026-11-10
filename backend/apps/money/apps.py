from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.money'
    label = 'money'
    default_auto_field = 'django.db.models.BigAutoField'
