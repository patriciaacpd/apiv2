from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'breathecode.payments'

    # def ready(self):
    #     from . import receivers
