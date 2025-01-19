"""
admin.py

Bu dosya, projedeki modellerin Django Admin panelinden yönetilmesini sağlar.
Kullanıcı dostu (alan grupları, description açıklamaları) ve geliştirici dostu
(docstring, anlaşılır alan isimleri) olacak şekilde tasarlanmıştır.

Modeller:
    - LogEntry
    - WhatsAppSettings
    - SmsSettings
    - SmtpSettings
    - GoogleApplicationsIntegration
    - SiteSettings
    - SocialMedia
    - HomePageSettings
    - FooterSettings
    - Menu
    - CustomUser (Genişletilmiş User Admin)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

# Modellerin importu
from .models import (
    LogEntry,
    WhatsAppSettings,
    SmsSettings,
    SmtpSettings,
    GoogleApplicationsIntegration,
    SocialMedia,
    CustomUser,
)


# -----------------------------------------------------------------------------
# LogEntry Admin
# -----------------------------------------------------------------------------
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """
    description: İşlem loglarını görüntülemek ve yönetmek için admin arayüzü.
    """
    list_display = ("id", "site", "user", "operation", "status", "timestamp")
    search_fields = ("user", "ip_address", "model_name", "operation", "status")
    ordering = ("-timestamp",)

    fieldsets = (
        ("Log Temel Bilgileri", {
            "fields": (
                "site",
                "user",
                "ip_address",
                "browser",
                "operating_system",
                "model_name",
                "operation",
                "status",
            ),
            "description": (
                "Bu bölümde logun hangi siteye ait olduğu, işlemi yapan kullanıcı, "
                "tarayıcı bilgisi ve yapılan işlemin türü gibi temel bilgiler bulunur."
            )
        }),
        ("Hash & Tarih", {
            "fields": (
                "hashed_data",
                "previous_hashed_data",
                "original_data",
                "timestamp",
            ),
            "description": (
                "Log verisinin bütünlüğünü sağlamak için kullanılan hash değerleri "
                "ve logun oluştuğu zaman bilgisi."
            )
        }),
    )


# -----------------------------------------------------------------------------
# WhatsAppSettings Admin
# -----------------------------------------------------------------------------
@admin.register(WhatsAppSettings)
class WhatsAppSettingsAdmin(admin.ModelAdmin):
    """
    description: WhatsApp API ayarlarını yönetmek için admin arayüzü.
    """
    list_display = ("id", "site", "apiUrl", "phoneNumber", "kontorMiktari")
    search_fields = ("apiUrl", "phoneNumber", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("API Bilgileri", {
            "fields": ("apiUrl", "apiKey"),
            "description": "WhatsApp API erişim adresi ve gerekli API anahtar bilgileri."
        }),
        ("Diğer Ayarlar", {
            "fields": ("phoneNumber", "kontorMiktari"),
            "description": "WhatsApp'a bağlı telefon numarası ve kalan kontör miktarı gibi bilgiler."
        }),
        ("Site & Zaman", {
            "fields": ("site",),
            "description": "Bu ayarların bağlı olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# SmsSettings Admin
# -----------------------------------------------------------------------------
@admin.register(SmsSettings)
class SmsSettingsAdmin(admin.ModelAdmin):
    """
    description: SMS API ayarlarını yönetmek için admin arayüzü.
    """
    list_display = ("id", "site", "url", "username", "kontorMiktari")
    search_fields = ("url", "username", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("API Bilgileri", {
            "fields": ("url", "username", "password"),
            "description": "SMS servisinin uç noktası (URL), kullanıcı adı ve şifresi."
        }),
        ("Kontör Bilgisi", {
            "fields": ("kontorMiktari",),
            "description": "SMS gönderebilmek için kalan kontör miktarını gösterir."
        }),
        ("Site & Zaman", {
            "fields": ("site",),
            "description": "Bu ayarların bağlı olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# SmtpSettings Admin
# -----------------------------------------------------------------------------
@admin.register(SmtpSettings)
class SmtpSettingsAdmin(admin.ModelAdmin):
    """
    description: E-posta (SMTP) ayarlarını yönetmek için admin arayüzü.
    """
    list_display = ("id", "site", "emailAddress", "smtpServer", "smtpPort", "useTls", "useSsl")
    search_fields = ("emailAddress", "smtpServer", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("Gönderici Bilgileri", {
            "fields": ("emailAddress",),
            "description": "E-postaların gönderileceği adresi belirtebilirsiniz."
        }),
        ("SMTP Sunucu Ayarları", {
            "fields": ("smtpServer", "smtpPort", "username", "password"),
            "description": (
                "SMTP sunucu adresi, portu ve yetkilendirme bilgileri. "
                "Örnek: smtp.gmail.com, 587."
            )
        }),
        ("Güvenlik Ayarları", {
            "fields": ("useTls", "useSsl"),
            "description": "TLS veya SSL kullanım tercihlerinizi belirleyebilirsiniz."
        }),
        ("Site & Zaman", {
            "fields": ("site",),
            "description": "Bu ayarların bağlı olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# GoogleApplicationsIntegration Admin
# -----------------------------------------------------------------------------
@admin.register(GoogleApplicationsIntegration)
class GoogleApplicationsIntegrationAdmin(admin.ModelAdmin):
    """
    description: Google uygulama kodlarının yönetimini kolaylaştırmak için admin arayüzü.
    """
    list_display = ("id", "site", "applicationType", "short_code_view")
    search_fields = ("applicationType", "site__domain")
    ordering = ("-updatedAt",)

    def short_code_view(self, obj):
        """
        Kısa kod görüntüsü, admin listesinde alanın çok uzun görünmesini önler.
        """
        return (obj.applicationCode[:50] + "...") if len(obj.applicationCode) > 50 else obj.applicationCode

    short_code_view.short_description = "Kod Önizleme"

    fieldsets = (
        ("Uygulama Seçimi", {
            "fields": ("applicationType",),
            "description": (
                "Google Webmasters, Analytics, Tag Manager, Adsense gibi "
                "hangi uygulamanın kullanılacağını belirtin."
            )
        }),
        ("Kod Bilgisi", {
            "fields": ("applicationCode",),
            "description": "Google uygulamasından aldığınız izleme/entegrasyon kodunu buraya ekleyin."
        }),
        ("Site & Zaman", {
            "fields": ("site",),
            "description": "Bu entegrasyonun bağlı olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# SiteSettings Admin + SocialMedia Inline
# -----------------------------------------------------------------------------
class SocialMediaInline(admin.TabularInline):
    """
    description: Siteye bağlı sosyal medya ikon/link bilgilerini tek ekrandan yönetir.
    Örnek:
        - icon: fab fa-facebook
        - link: https://facebook.com/ornek
    """
    model = SocialMedia
    extra = 1
    max_num = 7


class CustomSiteAdmin(SiteAdmin):
    inlines = [SocialMediaInline]


admin.site.unregister(Site)
admin.site.register(Site, CustomSiteAdmin)


# -----------------------------------------------------------------------------
# CustomUser Admin
# -----------------------------------------------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    description: Genişletilmiş kullanıcı modeli için admin arayüzü.
    Django'nun varsayılan UserAdmin'ini miras alır.
    """
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "isDealer")
    search_fields = ("username", "email", "phoneNumber", "mobilePhone")
    ordering = ("-date_joined",)

    fieldsets = (
        (_("Kullanıcı Bilgileri"), {
            "fields": (
                "username",
                "password",
                "first_name",
                "last_name",
                "email",
                "profilePicture",
            ),
            "description": (
                "Kullanıcının temel kimlik bilgilerini buradan düzenleyebilirsiniz. "
                "Örnek: Ad, Soyad, E-posta, Profil Resmi vb."
            )
        }),
        (_("İletişim ve Adres"), {
            "fields": (
                "phoneNumber",
                "mobilePhone",
                "address",
                "postalCode",
                "city",
                "district",
                "country",
            ),
            "description": "Kullanıcının iletişim ve adres bilgilerini buradan düzenleyebilirsiniz."
        }),
        (_("Ek Bilgiler"), {
            "fields": (
                "dateOfBirth",
                "isIndividual",
                "identificationNumber",
                "taxOffice",
                "companyName",
                "isEfatura",
                "secretQuestion",
                "secretAnswer",
                "smsPermission",
                "digitalMarketingPermission",
                "kvkkPermission",
            ),
            "description": (
                "Kullanıcının fatura bilgileri, gizli soru/cevap gibi özel alanlarını "
                "yönetebileceğiniz bölüm."
            )
        }),
        (_("Saat Dilimi ve Dil Tercihi"), {
            "fields": ("timezone", "preferred_language"),
            "description": "Kullanıcının saat dilimi ve tercih edilen dil ayarları."
        }),
        (_("Site ve Bayilik Bilgileri"), {
            "fields": ("selectedSite", "isDealer", "dealerID", "dealer_segment", "discountRate"),
            "description": (
                "Kullanıcının aktif olarak kullandığı siteyi, bayi durumunu, bayi indirim oranını "
                "ve ilişkili bayi segmentini ayarlayabileceğiniz alan."
            )
        }),
        (_("İzinler"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "description": "Django'nun yerleşik yetki/izin sistemine ilişkin alanlar."
        }),
        (_("Önemli Tarihler"), {
            "fields": ("last_login", "date_joined"),
            "description": "Kullanıcının son giriş yaptığı zaman ve hesap oluşturma tarihi."
        }),
    )
