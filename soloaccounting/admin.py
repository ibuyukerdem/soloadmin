from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site

from .forms import CustomAdminAuthenticationForm
from .models import ExtendedSite
from .models import SiteUrun, UserSite, WebServer, SqlServer, MailServer, DnsServer, \
    OperatingSystem, Product, CustomSiteConfiguration, CustomUser, Blacklist


class CustomAdminSite(AdminSite):
    login_form = CustomAdminAuthenticationForm


custom_admin_site = CustomAdminSite()

# Yönetim paneli URL'sini kullanacak şekilde güncelleyin
from django.urls import path

urlpatterns = [
    path('admin/', custom_admin_site.urls),
]

# Yönetim paneli başlıklarını `settings.py`'den alarak özelleştiriyoruz
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Yönetim Paneli')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Yönetim Paneli')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Hoş Geldiniz!')


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone', 'address', 'postalCode', 'city',
            'district', 'country', 'dateOfBirth', 'profilePicture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': (
            'isIndividual', 'identificationNumber', 'taxOffice', 'isEfatura', 'secretQuestion', 'secretAnswer', 'site',
            'smsPermission', 'digitalMarketingPermission', 'kvkkPermission')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')
        }),
    )

    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_active', 'isIndividual', 'isEfatura', 'smsPermission',
        'digitalMarketingPermission', 'kvkkPermission')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone')
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'serviceDuration', 'isActive', 'createdAt', 'updatedAt')
    list_filter = ('isActive',)
    search_fields = ('name',)
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


class SiteAdminForm(forms.ModelForm):
    is_active = forms.BooleanField(
        label="Active",
        required=False,
    )
    is_our_site = forms.BooleanField(
        label="Our Site",
        required=False,
    )
    show_popup_ad = forms.BooleanField(
        label="Show Popup Ad",
        required=False,
    )

    class Meta:
        model = Site
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Eğer bir kayıt düzenleniyorsa
            try:
                extended_site = self.instance.extended_site
                self.fields["is_active"].initial = extended_site.isActive
                self.fields["is_our_site"].initial = extended_site.isOurSite
                self.fields["show_popup_ad"].initial = extended_site.showPopupAd
            except ExtendedSite.DoesNotExist:
                self.fields["is_active"].initial = False
                self.fields["is_our_site"].initial = False
                self.fields["show_popup_ad"].initial = False


class SiteAdmin(admin.ModelAdmin):
    form = SiteAdminForm
    list_display = ("domain", "name", "is_active", "is_our_site", "show_popup_ad", "created_at", "updated_at")
    search_fields = ("domain", "name")

    def is_active(self, obj):
        return obj.extended_site.isActive if hasattr(obj, "extended_site") else None

    is_active.boolean = True
    is_active.short_description = "Active"

    def is_our_site(self, obj):
        return obj.extended_site.isOurSite if hasattr(obj, "extended_site") else None

    is_our_site.boolean = True
    is_our_site.short_description = "Our Site"

    def show_popup_ad(self, obj):
        return obj.extended_site.showPopupAd if hasattr(obj, "extended_site") else None

    show_popup_ad.boolean = True
    show_popup_ad.short_description = "Show Popup Ad"

    def created_at(self, obj):
        return obj.extended_site.createdAt if hasattr(obj, "extended_site") else None

    created_at.short_description = "Created At"

    def updated_at(self, obj):
        return obj.extended_site.updatedAt if hasattr(obj, "extended_site") else None

    updated_at.short_description = "Updated At"

    def save_model(self, request, obj, form, change):
        # Site modelini kaydet
        super().save_model(request, obj, form, change)
        # ExtendedSite için is_active, is_our_site ve show_popup_ad değerlerini formdan al
        is_active = form.cleaned_data.get("is_active", False)
        is_our_site = form.cleaned_data.get("is_our_site", False)
        show_popup_ad = form.cleaned_data.get("show_popup_ad", False)
        # ExtendedSite nesnesini oluştur veya güncelle
        extended_site, created = ExtendedSite.objects.get_or_create(site=obj)
        extended_site.isActive = is_active
        extended_site.isOurSite = is_our_site
        extended_site.showPopupAd = show_popup_ad
        extended_site.save()


# Site modelinin yeniden kaydedilmesi
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)


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


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'added_on', 'is_active')
    list_filter = ('is_active', 'added_on')
    search_fields = ('ip_address', 'reason')
    actions = ['activate_ips', 'deactivate_ips']

    def activate_ips(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Seçilen IP adresleri aktifleştirildi.")

    activate_ips.short_description = "Seçili IP'leri Aktifleştir"

    def deactivate_ips(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Seçilen IP adresleri pasifleştirildi.")

    deactivate_ips.short_description = "Seçili IP'leri Pasifleştir"
