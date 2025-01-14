"""
urls.py

Bu dosya, common/api/views.py içindeki ViewSet'lerin
router (url) yapılandırmasını içerir.

Swagger dokümantasyonu için:
    - /swagger/
    - /swagger.json
    - /swagger.yaml
gibi ek rotalar ekleyebilirsiniz.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LogEntryViewSet,
    WhatsAppSettingsViewSet,
    SmsSettingsViewSet,
    SmtpSettingsViewSet,
    GoogleApplicationsIntegrationViewSet,
    SiteSettingsViewSet,
    SocialMediaViewSet,
    HomePageSettingsViewSet,
    FooterSettingsViewSet,
    MenuViewSet,
    CustomUserViewSet
)

# DRF Router
router = DefaultRouter()
router.register(r"log-entries", LogEntryViewSet, basename="log-entries")
router.register(r"whatsapp-settings", WhatsAppSettingsViewSet, basename="whatsapp-settings")
router.register(r"sms-settings", SmsSettingsViewSet, basename="sms-settings")
router.register(r"smtp-settings", SmtpSettingsViewSet, basename="smtp-settings")
router.register(r"google-applications", GoogleApplicationsIntegrationViewSet, basename="google-applications")
router.register(r"site-settings", SiteSettingsViewSet, basename="site-settings")
router.register(r"social-media", SocialMediaViewSet, basename="social-media")
router.register(r"home-page-settings", HomePageSettingsViewSet, basename="home-page-settings")
router.register(r"footer-settings", FooterSettingsViewSet, basename="footer-settings")
router.register(r"menus", MenuViewSet, basename="menus")
router.register(r"users", CustomUserViewSet, basename="custom-users")

urlpatterns = [
    path("", include(router.urls)),
]
