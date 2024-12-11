from django.contrib import admin
from .models import GoogleApplicationsIntegration, SiteSettings, SmsSettings, SmtpSettings, WhatsAppSettings

class WhatsAppSettingsAdmin(admin.ModelAdmin):
    """
    WhatsApp Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = ('site', 'apiUrl', 'phoneNumber', 'kontorMiktari', 'createdAt', 'updatedAt')
    list_filter = ('site', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'apiUrl', 'phoneNumber')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'apiUrl', 'phoneNumber', 'apiKey', 'kontorMiktari')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )

admin.site.register(WhatsAppSettings, WhatsAppSettingsAdmin)

class SmtpSettingsAdmin(admin.ModelAdmin):
    """
    SMTP Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = (
        'site',
        'emailAddress',
        'smtpServer',
        'smtpPort',
        'username',
        'useTls',
        'useSsl',
        'createdAt',
        'updatedAt'
    )
    list_filter = ('site', 'useTls', 'useSsl', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'emailAddress', 'smtpServer', 'username')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'emailAddress', 'smtpServer', 'smtpPort', 'username', 'password', 'useTls', 'useSsl')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )

admin.site.register(SmtpSettings, SmtpSettingsAdmin)

class SmsSettingsAdmin(admin.ModelAdmin):
    """
    SMS Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = ('site', 'url', 'username', 'kontorMiktari', 'createdAt', 'updatedAt')
    list_filter = ('site', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'username', 'url')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'url', 'username', 'password', 'kontorMiktari')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )

admin.site.register(SmsSettings, SmsSettingsAdmin)


@admin.register(GoogleApplicationsIntegration)
class GoogleApplicationsIntegrationAdmin(admin.ModelAdmin):
    list_display = ('site', 'applicationType', 'createdAt', 'updatedAt')
    list_filter = ('applicationType', 'createdAt', 'updatedAt')
    search_fields = ('applicationType', 'site__name', 'applicationCode')
    ordering = ('-createdAt',)
    fieldsets = (
        (None, {
            'fields': ('site', 'applicationType', 'applicationCode')
        }),
        ('Tarih Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site', 'siteName', 'phone', 'gsm', 'email', 'updatedAt')
    list_filter = ('site', 'updatedAt')
    search_fields = ('site__name', 'siteName', 'email', 'phone', 'address')
    ordering = ('-updatedAt',)
    fieldsets = (
        ('Site Bilgileri', {
            'fields': ('site', 'siteName', 'metaTitle', 'metaDescription', 'logo')
        }),
        ('İletişim Bilgileri', {
            'fields': ('phone', 'gsm', 'email', 'address', 'googleMap')
        }),
        ('Politika ve Sözleşmeler', {
            'fields': ('cookiePolicy', 'privacyPolicy', 'termsOfUse', 'kvkkAgreement')
        }),
        ('Hakkımızda', {
            'fields': ('aboutUs',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')
