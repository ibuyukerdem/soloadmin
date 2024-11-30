# soloecommerce/apps.py
from django.apps import AppConfig

class SoloecommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloecommerce'
    verbose_name = "Solo E-Ticaret Platformu"
    description = "Ürün yönetimi, sipariş takibi ve online ticaret işlemlerini yöneten modül."

    def get_description(self):
        return self.description
