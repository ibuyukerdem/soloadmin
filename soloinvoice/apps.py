# soloinvoice/apps.py
from django.apps import AppConfig

class SoloinvoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloinvoice'
    verbose_name = "Solo Fatura Yönetim Sistemi"
    description = "Fatura oluşturma, takip etme ve muhasebe süreçlerini yöneten modül."

    def get_description(self):
        return self.description
