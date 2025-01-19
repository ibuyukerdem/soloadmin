from django.apps import AppConfig


class ServersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloaccounting.servers'
    verbose_name = "Server Yönetimi"
    description = "Server Tanımlamaları."
