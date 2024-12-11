import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from django.utils.timezone import localtime

from .forms import CustomAdminAuthenticationForm
from .models import ExtendedSite
from .models import SiteUrun, WebServer, SqlServer, MailServer, DnsServer, \
    OperatingSystem, Product, CustomSiteConfiguration, CustomUser, Blacklist, Menu, UserSite


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


# Form Özelleştirmesi: dealerID yalnızca bayi olan kullanıcıları gösterecek
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dealerID alanını özelleştiriyoruz
        self.fields['dealerID'].queryset = CustomUser.objects.filter(isDealer=True)


# CustomUserAdmin sınıfını özelleştiriyoruz
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm  # Formu özelleştirilmiş form ile bağlama

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone', 'address', 'postalCode', 'city',
            'district', 'country', 'dateOfBirth', 'profilePicture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': (
            'isIndividual', 'identificationNumber', 'taxOffice', 'isEfatura', 'secretQuestion', 'secretAnswer',
            'smsPermission', 'digitalMarketingPermission', 'kvkkPermission', 'isDealer', 'dealerID', 'discountRate')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'isDealer', 'dealerID',
                       'discountRate')
        }),
    )

    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_active', 'isIndividual', 'isEfatura',
        'smsPermission', 'digitalMarketingPermission', 'kvkkPermission', 'isDealer', 'dealerID', 'discountRate'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phoneNumber', 'mobilePhone')
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'serviceDuration', 'isActive', 'slug', 'createDate', 'updateDate')
    list_filter = ('isActive', 'createDate', 'updateDate')  # Filtreleme alanları
    search_fields = ('name', 'description')  # Arama alanları
    ordering = ('-createDate',)  # Varsayılan sıralama (Oluşturulma tarihine göre azalan)
    readonly_fields = ('createDate', 'updateDate', 'slug')  # Sadece okunabilir alanlar


class MenuAdminForm(forms.ModelForm):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("superuser", "Superuser"),
    ]

    roles = forms.MultipleChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Roles"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance.roles, list):
            self.fields["roles"].initial = self.instance.roles

    def clean_roles(self):
        return self.cleaned_data.get("roles", [])

    class Meta:
        model = Menu
        fields = "__all__"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm
    list_display = (
        'title',
        'path',
        'icon',
        'caption',
        'parent',
        'product',
        'order',
        'is_superuser_only',
        'disabled',
        'external'
    )  # `id` list_display'den kaldırıldı
    search_fields = ('title', 'path', 'icon', 'caption')  # Arama alanları
    list_filter = ('parent', 'product', 'is_superuser_only', 'disabled', 'external')  # Filtreleme
    ordering = ('order',)  # Sıralama
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'path',
                'icon',
                'caption',
                'parent',
                'product',
                'order'
            )
        }),
        ('Visibility & Access', {
            'fields': (
                'is_superuser_only',
                'roles',
                'disabled',
                'external'
            )
        }),
        ('Metadata', {
            'fields': ('info',)
        }),
    )


@admin.register(SiteUrun)
class SiteUrunAdmin(admin.ModelAdmin):
    list_display = ('site', 'urun_list', 'createdAt')
    search_fields = ('site__name', 'urun__name')
    list_filter = ('site',)
    filter_horizontal = ('urun',)

    def urun_list(self, obj):
        return ", ".join([urun.name for urun in obj.urun.all()])

    urun_list.short_description = "Ürünler"


def safe_remove(file_path):
    """
    Dosyayı güvenli bir şekilde siler. Dosya mevcut değilse hata vermez.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Silindi: {file_path}")


class SiteAdminForm(forms.ModelForm):
    """
    Site admini için form.
    """
    is_active = forms.BooleanField(label="Aktif", required=False)
    is_our_site = forms.BooleanField(label="Bizim Sitemiz", required=False)
    is_default_site = forms.BooleanField(label="Varsayılan Site", required=False)
    show_popup_ad = forms.BooleanField(label="Pop-up Reklam Gösterimi", required=False)
    logo = forms.ImageField(label="Site Logosu", required=False)

    def clean_logo(self):
        """
        Admin panelinden 'logo' alanı temizlendiğinde fiziksel dosyayı da siler ve veritabanı kaydını temizler.
        """
        logo = self.cleaned_data.get("logo", None)

        # ExtendedSite ile bağlantılı olan logo alanını kontrol edin
        if self.instance.pk:
            extended_site = getattr(self.instance, "extended_site", None)
            if extended_site and not logo and extended_site.logo:
                # Logo temizlenmişse fiziksel dosyayı sil
                safe_remove(extended_site.logo.path)
                extended_site.logo = None  # Veritabanındaki logo alanını temizle
                extended_site.save()  # Değişiklikleri kaydet

        return logo

    class Meta:
        model = Site
        fields = "__all__"

    def clean_logo(self):
        """
        Admin panelinden 'logo' alanı temizlendiğinde fiziksel dosyayı da siler ve veritabanı kaydını temizler.
        """
        logo = self.cleaned_data.get("logo", None)

        # ExtendedSite ile bağlantılı olan logo alanını kontrol edin
        if self.instance.pk:
            extended_site = getattr(self.instance, "extended_site", None)
            if extended_site and not logo and extended_site.logo:
                # Logo temizlenmişse fiziksel dosyayı sil
                safe_remove(extended_site.logo.path)
                extended_site.logo = None  # Veritabanındaki logo alanını temizle
                extended_site.save()  # Değişiklikleri kaydet

        return logo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extended_site = getattr(self.instance, "extended_site", None)
        if extended_site:
            self.fields["is_active"].initial = extended_site.isActive
            self.fields["is_our_site"].initial = extended_site.isOurSite
            self.fields["is_default_site"].initial = extended_site.isDefault
            self.fields["show_popup_ad"].initial = extended_site.showPopupAd
            if extended_site.logo:
                self.fields["logo"].initial = extended_site.logo


class SiteAdmin(admin.ModelAdmin):
    """
    Site modeli için admin yapılandırması.
    """
    form = SiteAdminForm
    list_display = (
        "domain", "name", "is_active", "is_our_site", "is_default", "show_popup_ad",
        "formatted_created_at", "formatted_updated_at"  # Tarih alanları listede görünür
    )
    readonly_fields = ("formatted_created_at", "formatted_updated_at")  # Detay görünümünde yalnızca okunabilir alanlar
    search_fields = ("domain", "name")

    def is_active(self, obj):
        return getattr(obj.extended_site, "isActive", False)

    is_active.boolean = True
    is_active.short_description = "Aktif"

    def is_our_site(self, obj):
        return getattr(obj.extended_site, "isOurSite", False)

    is_our_site.boolean = True
    is_our_site.short_description = "Bizim Sitemiz"

    def is_default(self, obj):
        return getattr(obj.extended_site, "isDefault", False)

    is_default.boolean = True
    is_default.short_description = "Varsayılan Site"

    def show_popup_ad(self, obj):
        return getattr(obj.extended_site, "showPopupAd", False)

    show_popup_ad.boolean = True
    show_popup_ad.short_description = "Pop-up Reklam"

    def logo_display(self, obj):
        extended_site = obj.extended_site
        if extended_site and extended_site.logo:
            return f'<img src="{extended_site.logo.url}" style="width:48px; height:auto;" alt="Logo"/>'
        return "Logo Yok"

    logo_display.short_description = "Logo"
    logo_display.allow_tags = True

    def formatted_created_at(self, obj):
        """
        Oluşturulma tarihini okunabilir formatta döndürür.
        """
        extended_site = getattr(obj, "extended_site", None)
        if extended_site and extended_site.createdAt:
            return localtime(extended_site.createdAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_created_at.short_description = "Oluşturulma Tarihi"

    def formatted_updated_at(self, obj):
        """
        Güncellenme tarihini okunabilir formatta döndürür.
        """
        extended_site = getattr(obj, "extended_site", None)
        if extended_site and extended_site.updatedAt:
            return localtime(extended_site.updatedAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_updated_at.short_description = "Güncellenme Tarihi"

    def save_model(self, request, obj, form, change):
        """
        Site modeli kaydedildiğinde ExtendedSite modelini de günceller veya oluşturur.
        """
        super().save_model(request, obj, form, change)
        extended_site, _ = ExtendedSite.objects.get_or_create(site=obj)
        extended_site.isActive = form.cleaned_data.get("is_active", False)
        extended_site.isOurSite = form.cleaned_data.get("is_our_site", False)
        extended_site.isDefault = form.cleaned_data.get("is_default_site", False)
        extended_site.showPopupAd = form.cleaned_data.get("show_popup_ad", False)

        if "logo" in form.cleaned_data:
            if not form.cleaned_data["logo"]:
                if extended_site.logo:
                    safe_remove(extended_site.logo.path)
                extended_site.logo = None
            else:
                extended_site.logo = form.cleaned_data["logo"]

        extended_site.save()


# Site modelini yeni admin yapılandırmasıyla kaydetme
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


@admin.register(UserSite)
class UserSiteAdmin(admin.ModelAdmin):
    list_display = ("user", "site", "createdAt", "updatedAt")
    list_filter = ("site", "user")
    search_fields = ("user__username", "site__name")
    readonly_fields = ("createdAt", "updatedAt")
