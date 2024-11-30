# soloservice/apps.py
from django.apps import AppConfig

class SoloserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloservice'
    verbose_name = "Solo Araç Servis Yönetim Sistemi"
    description = "Araç bakım, onarım ve iş emri süreçlerini yöneten modül."

    def get_description(self):
        return self.description
