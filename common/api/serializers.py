"""
serializers.py

Bu dosya, common/models.py içinde tanımlanmış modeller için
DRF serializer sınıflarını barındırır.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from common.models import (
    LogEntry,
    WhatsAppSettings,
    SmsSettings,
    SmtpSettings,
    GoogleApplicationsIntegration,
    SiteSettings,
    SocialMedia,
    HomePageSettings,
    FooterSettings,
    Menu
)


# -----------------------------------------------------------------------------
# LogEntry Serializer
# -----------------------------------------------------------------------------
class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = "__all__"
        read_only_fields = (
            "hashed_data",
            "previous_hashed_data",
            "timestamp",
        )


# -----------------------------------------------------------------------------
# WhatsAppSettings Serializer
# -----------------------------------------------------------------------------
class WhatsAppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# SmsSettings Serializer
# -----------------------------------------------------------------------------
class SmsSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# SmtpSettings Serializer
# -----------------------------------------------------------------------------
class SmtpSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmtpSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# GoogleApplicationsIntegration Serializer
# -----------------------------------------------------------------------------
class GoogleApplicationsIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleApplicationsIntegration
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# SiteSettings Serializer
# -----------------------------------------------------------------------------
class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# SocialMedia Serializer
# -----------------------------------------------------------------------------
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# HomePageSettings Serializer
# -----------------------------------------------------------------------------
class HomePageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePageSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# FooterSettings Serializer
# -----------------------------------------------------------------------------
class FooterSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterSettings
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )


# -----------------------------------------------------------------------------
# Menu Serializer
# -----------------------------------------------------------------------------
class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"
        read_only_fields = (
            "createdAt",
            "updatedAt",
        )
        ref_name = "CommonMenu"


# -----------------------------------------------------------------------------
# CustomUser Serializer
# -----------------------------------------------------------------------------
User = get_user_model()  # Bu, CustomUser olabilir.

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        # Örnek: read_only_fields ekleyebilirsiniz
        read_only_fields = (
            "last_login",
            "date_joined",
            "password",  # Parolayı dışarıya açmak istemezseniz.
        )
        # Parola güncelleme gibi işlemler için özel yaklaşımlar kullanılabilir.
