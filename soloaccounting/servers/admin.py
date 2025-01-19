# soloaccounting/servers/admin.py
from django.contrib import admin
from django.utils.timezone import localtime
from .models import WebServer, SqlServer, MailServer, DnsServer, \
    OperatingSystem, CustomSiteConfiguration


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "createdAt", "updatedAt")
    search_fields = ("name", "version")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("name", "version")}),
        ("Açıklama", {"fields": ("description",)}),
        ("Tarih Bilgileri", {"fields": ("createdAt", "updatedAt")}),
    )


@admin.register(WebServer)
class WebServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(SqlServer)
class SqlServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(MailServer)
class MailServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(DnsServer)
class DnsServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(CustomSiteConfiguration)
class CustomSiteConfigurationAdmin(admin.ModelAdmin):
    """
    Site konfigürasyonlarını yönetir.
    """
    list_display = (
        "site", "webServer", "sqlServer", "mailServer", "dnsServer", "formatted_created_at", "formatted_updated_at")
    list_filter = ("site", "webServer", "sqlServer", "mailServer", "dnsServer")
    search_fields = ("site__name", "webServer__domain", "sqlServer__domain", "mailServer__domain", "dnsServer__domain")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {
            "fields": ("site",),
            "description": "Bu konfigürasyonun ait olduğu siteyi belirtin."
        }),
        ("Sunucu Konfigürasyonları", {
            "fields": ("webServer", "sqlServer", "mailServer", "dnsServer"),
            "description": "Siteye bağlı sunucu yapılandırmalarını seçin."
        }),
        ("Tarih Bilgileri", {
            "fields": ("createdAt", "updatedAt"),
            "description": "Konfigürasyonun oluşturulma ve güncellenme tarihleri."
        }),
    )

    def formatted_created_at(self, obj):
        if obj.createdAt:
            return localtime(obj.createdAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_created_at.short_description = "Oluşturulma Tarihi"

    def formatted_updated_at(self, obj):
        if obj.updatedAt:
            return localtime(obj.updatedAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_updated_at.short_description = "Güncellenme Tarihi"
