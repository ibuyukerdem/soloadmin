import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.urls import path
from django.utils.timezone import localtime

from .forms import CustomAdminAuthenticationForm
from .models import ExtendedSite
from .models import SiteUrun, Blacklist, Menu, Product, Category, Currency


class CustomAdminSite(AdminSite):
    login_form = CustomAdminAuthenticationForm


custom_admin_site = CustomAdminSite()

# Yönetim paneli URL'sini kullanacak şekilde güncelleyin


urlpatterns = [
    path('admin/', custom_admin_site.urls),
]

# Yönetim paneli başlıklarını `settings.py`'den alarak özelleştiriyoruz
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Yönetim Paneli')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Yönetim Paneli')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Hoş Geldiniz!')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """
    Bu yönetim ekranı, sisteminizde kullanılan para birimlerini düzenlemenizi ve listelemenizi sağlar.
    Kullanıcı dostu açıklamalar sayesinde, yöneticiler değişiklik yaparken neyin ne anlama geldiğini kolayca anlayabilir.
    """

    # Admin panelinde gözükecek alanlar
    list_display = (
        'code',
        'name',
        'exchange_rate',
        'is_default'
    )

    # Üzerine tıklanabilir alan
    list_display_links = ('code', 'name',)

    # Kayıtlarda hızlı arama yaparken kullanılacak alanlar
    search_fields = ('code', 'name',)

    # Değişiklik formunda gruplama yaparak kullanıcıya açıklayıcı bir düzen sunuyoruz
    fieldsets = (
        ("Genel Bilgiler", {
            'description': "Burada para biriminin temel kimlik bilgilerini düzenleyebilirsiniz.",
            'fields': ('code', 'name')
        }),
        ("Dönüşüm Bilgileri", {
            'description': "Bu bölümde para birimini varsayılan para birimine çevirirken kullanılacak oranlar yer almaktadır.",
            'fields': ('exchange_rate', 'is_default')
        }),
    )

    # Filtreleme seçenekleri ile kullanıcının yönetim panelinde kayıtları hızlıca filtrelemesini sağlayın
    list_filter = ('is_default',)

    # Kayıt yapıldığında veya güncellendiğinde kullanıcıya basit bir mesaj gösterebilirsiniz (opsiyonel)
    save_on_top = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'parent', 'slug'),
            'description': (
                "Kategori adını ve açıklamasını girin. Üst kategori seçerek hiyerarşik yapı oluşturabilirsiniz. "
                "Slug otomatik oluşturulur, gerekirse elle düzenleyebilirsiniz."
            )
        }),
    )
    # Bu sayede kategorileri hiyerarşik olarak yönetebilir, arama ve filtreleme yapabilirsiniz.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'currency', 'serviceDuration', 'isActive', 'createDate', 'updateDate')
    list_filter = ('isActive', 'category', 'currency')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'createDate', 'updateDate')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category'),
            'description': (
                "Ürün temel bilgilerini girin. İsim, açıklama ve kategorisini belirtin. "
                "Kategori seçerek müşterilerin bu ürünü ilgili kategoride bulmasını kolaylaştırın."
            )
        }),
        ("Fiyat & Süre", {
            'fields': ('serviceDuration', 'price', 'currency', 'isActive'),
            'description': (
                "Hizmet süresi (ay) ve fiyat bilgilerini girin. Ürün pasifse sitede görünmez. "
                "Ayrıca fiyatın belirtilmekte olduğu para birimini seçin. Örneğin, bir blog yazılımı için "
                "hizmet süresi 12 ay olabilir, fiyatı 100 EUR veya 2000 TRY şeklinde girebilir, "
                "para birimi alanından da EUR veya TRY seçebilirsiniz."
            )
        }),
        ("URL Bilgileri", {
            'fields': ('slug',),
            'description': "Ürünün URL yapısını otomatik oluşturur. Genellikle değiştirmeye gerek yok."
        }),
        ("Tarih Bilgileri", {
            'fields': ('createDate', 'updateDate'),
            'description': "Oluşturulma ve güncellenme tarihleri otomatik ayarlanır."
        }),
    )


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

@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    """
    Karalisteye alınan IP adreslerini yönetir.
    """
    list_display = ("ip_address", "reason", "added_on", "is_active")
    list_filter = ("is_active", "added_on")
    search_fields = ("ip_address", "reason")
    fieldsets = (
        (None, {
            "fields": ("ip_address", "reason", "is_active"),
            "description": "Karalisteye alınacak IP adresi ve nedeni."
        }),
        ("Tarih Bilgileri", {
            "fields": ("added_on",),
            "description": "IP'nin ne zaman karalisteye alındığı bilgisi.",
        }),
    )
    readonly_fields = ("added_on",)


