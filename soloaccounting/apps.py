# soloaccounting/apps.py
from django.apps import AppConfig

class SoloaccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloaccounting'
    verbose_name = "Solo Müşteri Yönetimi"
    description = "Müşteri firma kaydı, lisans yönetimi, modül yönetiminin yapıldığı app."

    def get_description(self):
        return self.description
