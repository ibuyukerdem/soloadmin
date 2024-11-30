# solofinance/apps.py
from django.apps import AppConfig

class SolofinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solofinance'
    verbose_name = "Solo Finans Yönetim Sistemi"
    description = "Müşteri finansal işlemleri ve gelir-gider takibini yöneten modül."

    def get_description(self):
        return self.description
