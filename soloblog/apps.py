# soloblog/apps.py
from django.apps import AppConfig

class SoloblogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloblog'
    verbose_name = "Solo Blog Yönetim Sistemi"
    description = "SEO odaklı blog içeriklerinin oluşturulması, yayınlanması ve yönetimini sağlayan modül."

    def get_description(self):
        return self.description
