from django.contrib import admin
from .models import GoogleApplicationsIntegration, SiteSettings


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
