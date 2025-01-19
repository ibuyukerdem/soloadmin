from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soloaccounting.campaigns'
    verbose_name = "Kampanya ve Bayi Yönetimi"
    description = "Kampanya tanımlamaları ve bayi tanımlamaları burada yapılır."
