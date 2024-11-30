from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site

from .models import Module, SiteUrun, UserSite, WebServer, SqlServer, MailServer, DnsServer, \
    OperatingSystem, Product, Service, CustomSiteConfiguration, CustomUser

# Yönetim paneli başlıklarını `settings.py`'den alarak özelleştiriyoruz
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Yönetim Paneli')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Yönetim Paneli')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Hoş Geldiniz!')


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone', 'address', 'postalCode', 'city', 'district', 'country', 'dateOfBirth', 'profilePicture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': ('isIndividual', 'identificationNumber', 'taxOffice', 'isEfatura', 'secretQuestion', 'secretAnswer', 'site', 'smsPermission', 'digitalMarketingPermission', 'kvkkPermission')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'isIndividual', 'isEfatura', 'smsPermission', 'digitalMarketingPermission', 'kvkkPermission')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'serviceDuration', 'isActive', 'createdAt', 'updatedAt')
    list_filter = ('isActive',)
    search_fields = ('name',)
    ordering = ('-createdAt',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'price', 'serviceDuration', 'isActive', 'createdAt', 'updatedAt')
    list_filter = ('isActive', 'product')
    search_fields = ('name', 'product__name')
    ordering = ('-createdAt',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'price', 'serviceDuration', 'isActive', 'createdAt', 'updatedAt')
    list_filter = ('isActive', 'product')
    search_fields = ('name', 'product__name')
    ordering = ('-createdAt',)


@admin.register(SiteUrun)
class SiteUrunAdmin(admin.ModelAdmin):
    list_display = ('site', 'urun_list', 'createdAt')
    search_fields = ('site__name', 'urun__name')
    list_filter = ('site',)
    filter_horizontal = ('urun',)

    def urun_list(self, obj):
        return ", ".join([urun.name for urun in obj.urun.all()])

    urun_list.short_description = "Ürünler"


@admin.register(UserSite)
class UserSiteAdmin(admin.ModelAdmin):
    list_display = ('user', 'site', 'createdAt')
    search_fields = ('user__username', 'site__name', 'site__domain')
    list_filter = ('site', 'createdAt')
    ordering = ('-createdAt',)
    autocomplete_fields = ('site',)


# Önce mevcut kaydı kaldırıyoruz
admin.site.unregister(Site)


# Varsayılan Site modeline özelleştirme
@admin.register(Site)
class CustomSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domain')
    search_fields = ('name', 'domain')


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
    list_display = ('site', 'webServer', 'sqlServer', 'mailServer', 'dnsServer', 'createdAt', 'updatedAt')
    list_filter = ('webServer', 'sqlServer', 'mailServer', 'dnsServer')
    search_fields = ('site__name', 'webServer__name', 'sqlServer__name', 'mailServer__name', 'dnsServer__name')
    ordering = ('-createdAt',)
