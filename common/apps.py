# common/apps.py
from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    verbose_name = "Ortak Uygulamalar"
    description = "Genel işlevlerin ve paylaşılan modüllerin bulunduğu uygulama."

    def get_description(self):
        return self.description
