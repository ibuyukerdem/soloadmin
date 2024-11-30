# solopayment/apps.py
from django.apps import AppConfig

class SolopaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solopayment'
    verbose_name = "Solo Tahsilat Sistemi"
    description = "Sanal pos ile tahsilat yönetimi yapılan modül."

    def get_description(self):
        return self.description
