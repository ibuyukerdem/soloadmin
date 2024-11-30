# soloweb/apps.py
from django.apps import AppConfig

class SolowebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloweb'
    verbose_name = "Solo Web Yönetim Sistemi"
    description = "Firma web sitelerinin içerik yönetimi ve müşteri etkileşimlerini yöneten modül."

    def get_description(self):
        return self.description
