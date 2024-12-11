# Model Açıklaması:
# Bu model, projemizdeki her veri kaydının bir siteyle ilişkilendirilmesini sağlamak için
# `common.models.AbstractBaseModel` sınıfını miras alır. Bu sınıf, aşağıdaki alanları içerir:
# 1. `site`: Kaydın hangi siteye ait olduğunu belirtir (`ForeignKey(Site)`).
# 2. `created_at`: Kaydın oluşturulma tarihi (`DateTimeField`).
# 3. `updated_at`: Kaydın son güncellenme tarihi (`DateTimeField`).
#
# AbstractBaseModel kullanılarak, tekrarlayan kodlar minimize edilmiş ve verilerin çoklu site
# desteği için yapılandırılması sağlanmıştır.

# class ExampleModel(AbstractBaseModel):
#     """
#     Örnek model, AbstractBaseModel'i miras alarak `site`, `created_at` ve `updated_at` alanlarına sahiptir.
#     """
#     name = models.CharField(max_length=255, help_text="Modelin adı")
#     description = models.TextField(help_text="Modelin açıklaması")
#
#     def __str__(self):
#         return self.name


import os
import uuid

from PIL import Image, ImageOps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from common.models import AbstractBaseModel

ALLOWED_FORMATS = ["JPEG", "JPG", "PNG", "WEBP"]

def logo_upload_path(instance, filename):
    directory = f'logos/site_{instance.site.id}'
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, directory)):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, directory), exist_ok=True)

    # Benzersiz bir dosya adı oluştur
    ext = filename.split('.')[-1]  # Dosya uzantısını al
    unique_filename = f"{uuid.uuid4().hex}.{ext}"  # UUID ile benzersiz ad oluştur
    return os.path.join(directory, unique_filename)


def safe_remove(file_path):
    """
    Dosyayı güvenli bir şekilde siler. Dosya mevcut değilse hata vermez.
    """
    if os.path.exists(file_path):
        os.remove(file_path)


class ExtendedSite(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="extended_site",
        verbose_name="Site",
        help_text="Bağlı olduğu siteyi seçin."
    )
    createdAt = models.DateTimeField(
        "Oluşturulma Tarihi",
        auto_now_add=True,
        help_text="Kayıt oluşturulma tarihi otomatik olarak eklenir."
    )
    updatedAt = models.DateTimeField(
        "Güncellenme Tarihi",
        auto_now=True,
        help_text="Son güncellenme tarihi otomatik olarak eklenir."
    )
    isActive = models.BooleanField(
        "Aktif",
        default=True,
        help_text="Bu site aktif mi? Aktif olmayan siteler listelerde gösterilmez."
    )
    isOurSite = models.BooleanField(
        "Bizim Sitemiz",
        default=False,
        help_text="Bu site bizim tarafımızdan kontrol ediliyorsa işaretleyin."
    )
    showPopupAd = models.BooleanField(
        "Pop-up Reklam Gösterimi",
        default=False,
        help_text="Bu sitede pop-up reklam göstermek istiyorsanız işaretleyin."
    )
    isDefault = models.BooleanField(
        "Varsayılan Site",
        default=False,
        help_text="Bu site varsayılan olarak seçilsin mi?"
    )
    logo = models.ImageField(
        upload_to=logo_upload_path,
        verbose_name="Site Logosu",
        help_text="Site için bir logo yükleyin. Görüntü otomatik olarak 48x48 piksel ve kare formatına uygun hale getirilir.",
        default="logos/default_logo.webp"
    )

    class Meta:
        verbose_name = "Genişletilmiş Site"
        verbose_name_plural = "Genişletilmiş Siteler"

    def __str__(self):
        return self.site.name

    def delete(self, *args, **kwargs):
        """
        Model silindiğinde logo dosyasını da fiziksel olarak siler.
        """
        if self.logo:
            safe_remove(self.logo.path)  # Dosya fiziksel olarak silinir
        super().delete(*args, **kwargs)

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

        # Logo kontrolü: Eğer logo temizlenmişse fiziksel ve veritabanı kaydını temizle
        if "logo" in form.cleaned_data:
            if not form.cleaned_data["logo"]:  # Logo alanı temizlenmişse
                safe_remove(extended_site.logo.path)
                extended_site.logo = None
            else:
                extended_site.logo = form.cleaned_data["logo"]

        extended_site.save()


class Product(models.Model):
    """
    Product modeli, ürünlerin temel özelliklerini barındırır.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Ürün Adı",
        help_text="Ürün adını belirtiniz."
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="Ürünün URL'de kullanılacak kısa adı. Otomatik oluşturulur.",
        blank=True
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Ürün Açıklaması",
        help_text="Ürün ile ilgili açıklama."
    )
    serviceDuration = models.PositiveIntegerField(
        verbose_name="Hizmet Süresi (Ay)",
        help_text="Hizmet süresi ay cinsinden belirtilmelidir."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ürün Fiyatı",
        help_text="Ürün fiyatını belirtiniz."
    )
    isActive = models.BooleanField(
        default=True,
        verbose_name="Aktif",
        help_text="Ürünün aktif/pasif durumunu belirtir."
    )
    createDate = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi",
        help_text="Bu kaydın oluşturulma tarihi otomatik olarak ayarlanır."
    )
    updateDate = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi",
        help_text="Bu kaydın son güncellenme tarihi otomatik olarak ayarlanır."
    )

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


class Menu(models.Model):
    title = models.CharField(max_length=100)
    path = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Iconify ikon adı. Örn: 'material-symbols:shopping-cart'"
    )
    caption = models.CharField(max_length=255, blank=True, null=True, default=None)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', blank=True, null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='menus', blank=True, null=True
    )
    order = models.PositiveIntegerField(default=0, help_text="Menü sıralaması")
    roles = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        help_text="Bu menüye erişimi olan roller listesi. Örn: ['admin', 'manager']"
    )
    info = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text="Menü öğesi için bilgi (örneğin bir etiket)"
    )
    disabled = models.BooleanField(
        default=False,
        help_text="Menü öğesinin devre dışı olup olmadığını belirtir"
    )
    external = models.BooleanField(
        default=False,
        help_text="Harici bir bağlantı olup olmadığını belirtir"
    )
    is_superuser_only = models.BooleanField(
        default=False,
        help_text="Bu menü yalnızca superuser tarafından görülebilir."
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Menü Öğesi"
        verbose_name_plural = "Menü Öğeleri"

    def __str__(self):
        return self.title


# bu model ile sitelerin ürün eşleşmeleri yapılıyor bir siteye birden falla ürün eklenebilir hale geliyor
class SiteUrun(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name="urunSite", verbose_name="Site")
    urun = models.ManyToManyField(Product, related_name="siteUrun", verbose_name="Ürünler")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Site Ürün Eşleşmesi"
        verbose_name_plural = "Site Ürün Eşleşmeleri"

    def __str__(self):
        return f"{self.site.name} - {', '.join([urun.name for urun in self.urun.all()])}"


# kullanıcıların belirli sitelerle olan ilişkisi burada tanımlıyoruz
class UserSite(AbstractBaseModel):
    """
    UserSite modeli, kullanıcıların belirli sitelerle olan ilişkisini temsil eder.
    AbstractBaseModel'i miras alarak `site`, `created_at` ve `updated_at` alanlarını içerir.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userSites",
        verbose_name="Kullanıcı"
    )

    class Meta:
        verbose_name = "Kullanıcı-Site İlişkisi"
        verbose_name_plural = "Kullanıcı-Site İlişkileri"

    def __str__(self):
        return f"{self.user.username} - {self.site.name}"


class CustomUser(AbstractUser):
    phoneNumber = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefon Numarası')
    mobilePhone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Mobil Telefon')
    address = models.TextField(blank=True, null=True, verbose_name='Adres')
    postalCode = models.CharField(max_length=20, blank=True, null=True, verbose_name='Posta Kodu')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Şehir')
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name='İlçe')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ülke')
    dateOfBirth = models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')
    profilePicture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Profil Resmi'
    )
    isIndividual = models.BooleanField(default=True, verbose_name='Kurumsal Fatura İstiyorum')
    identificationNumber = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='TC Kimlik/Vergi Numarası'
    )
    taxOffice = models.CharField(max_length=100, blank=True, null=True, verbose_name='Vergi Dairesi')
    companyName = models.CharField(max_length=255, blank=True, null=True, verbose_name='Şirket/Kuruluş Adı')
    isEfatura = models.BooleanField(default=False, verbose_name='e-Fatura Mükellefi')
    secretQuestion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Gizli Soru')
    secretAnswer = models.CharField(max_length=255, blank=True, null=True, verbose_name='Gizli Cevap')
    smsPermission = models.BooleanField(default=False, verbose_name='SMS İzni')
    digitalMarketingPermission = models.BooleanField(default=False, verbose_name='Dijital Pazarlama İzni')
    kvkkPermission = models.BooleanField(default=False, verbose_name='KVKK İzni')

    dealerID = models.ForeignKey(
        'self',  # Modelin kendisine referans
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'isDealer': True},  # Sadece isDealer=True olanlar
        verbose_name='Bayi'
    )
    isDealer = models.BooleanField(default=False, verbose_name='Bayi Mi?')  # Bayi olup olmadığını belirtir
    discountRate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='İskonto Oranı'
    )  # İskonto oranı (ör. 5.25% gibi)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        verbose_name='Gruplar'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        verbose_name='Kullanıcı İzinleri'
    )

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return self.username


# Server işletim sistemi tanımları buraya yappılıyor
class OperatingSystem(AbstractBaseModel):
    """
    OperatingSystem modeli, AbstractBaseModel'i miras alarak `site`, `created_at` ve `updated_at` alanlarına sahiptir.
    """
    name = models.CharField(max_length=100, verbose_name="İşletim Sistemi Adı")
    version = models.CharField(max_length=50, verbose_name="Versiyon", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)

    class Meta:
        verbose_name = "S-İşletim Sistemi"
        verbose_name_plural = "S-İşletim Sistemleri"

    def __str__(self):
        return f"{self.name} {self.version}"


class PaymentType(models.TextChoices):
    MONTHLY = "Monthly", "Aylık"
    YEARLY = "Yearly", "Yıllık"


# Web sunucularımızı buraya tanımlıyoruz
class WebServer(AbstractBaseModel):
    operatingSystem = models.ForeignKey(
        OperatingSystem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşletim Sistemi"
    )
    domain = models.CharField(max_length=255, verbose_name="Domain", null=True, blank=True)
    ns1 = models.CharField(max_length=255, verbose_name="NS1", null=True, blank=True)
    ns2 = models.CharField(max_length=255, verbose_name="NS2", null=True, blank=True)
    ipAddress1 = models.GenericIPAddressField(verbose_name="Web Sunucusu IP 1", null=True, blank=True)
    ipAddress2 = models.GenericIPAddressField(verbose_name="Web Sunucusu IP 2", null=True, blank=True)
    ipAddress3 = models.GenericIPAddressField(verbose_name="Web Sunucusu IP 3", null=True, blank=True)
    ipAddress4 = models.GenericIPAddressField(verbose_name="Web Sunucusu IP 4", null=True, blank=True)
    ipAddress5 = models.GenericIPAddressField(verbose_name="Web Sunucusu IP 5", null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Kullanıcı Adı", null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name="Şifre", null=True, blank=True)
    paymentType = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.MONTHLY, verbose_name="Ödeme Tipi"
    )
    priceUsd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ücret (USD)", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Sunucunun aktif/pasif durumunu belirtir.")
    isDefault = models.BooleanField(default=False, verbose_name="Varsayılan",
                                    help_text="Bu sunucunun varsayılan olup olmadığını belirtir.")

    class Meta:
        verbose_name = "S-Web Sunucusu"
        verbose_name_plural = "S-Web Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} Web Sunucusu"


# SQL sunucularımızı buraya tanımlıyoruz
class SqlServer(AbstractBaseModel):
    operatingSystem = models.ForeignKey(
        OperatingSystem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşletim Sistemi"
    )
    domain = models.CharField(max_length=255, verbose_name="Domain", null=True, blank=True)
    ns1 = models.CharField(max_length=255, verbose_name="NS1", null=True, blank=True)
    ns2 = models.CharField(max_length=255, verbose_name="NS2", null=True, blank=True)
    ipAddress1 = models.GenericIPAddressField(verbose_name="SQL Sunucusu IP 1", null=True, blank=True)
    ipAddress2 = models.GenericIPAddressField(verbose_name="SQL Sunucusu IP 2", null=True, blank=True)
    ipAddress3 = models.GenericIPAddressField(verbose_name="SQL Sunucusu IP 3", null=True, blank=True)
    ipAddress4 = models.GenericIPAddressField(verbose_name="SQL Sunucusu IP 4", null=True, blank=True)
    ipAddress5 = models.GenericIPAddressField(verbose_name="SQL Sunucusu IP 5", null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Kullanıcı Adı", null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name="Şifre", null=True, blank=True)
    paymentType = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.MONTHLY, verbose_name="Ödeme Tipi"
    )
    priceUsd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ücret (USD)", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Sunucunun aktif/pasif durumunu belirtir.")
    isDefault = models.BooleanField(default=False, verbose_name="Varsayılan",
                                    help_text="Bu sunucunun varsayılan olup olmadığını belirtir.")

    class Meta:
        verbose_name = "S-SQL Sunucusu"
        verbose_name_plural = "S-SQL Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} SQL Sunucusu"


# mail sunucularımzı buraya tanımlıyoruz
class MailServer(AbstractBaseModel):
    operatingSystem = models.ForeignKey(
        OperatingSystem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşletim Sistemi"
    )
    domain = models.CharField(max_length=255, verbose_name="Domain", null=True, blank=True)
    ns1 = models.CharField(max_length=255, verbose_name="NS1", null=True, blank=True)
    ns2 = models.CharField(max_length=255, verbose_name="NS2", null=True, blank=True)
    ipAddress1 = models.GenericIPAddressField(verbose_name="Mail Sunucusu IP 1", null=True, blank=True)
    ipAddress2 = models.GenericIPAddressField(verbose_name="Mail Sunucusu IP 2", null=True, blank=True)
    ipAddress3 = models.GenericIPAddressField(verbose_name="Mail Sunucusu IP 3", null=True, blank=True)
    ipAddress4 = models.GenericIPAddressField(verbose_name="Mail Sunucusu IP 4", null=True, blank=True)
    ipAddress5 = models.GenericIPAddressField(verbose_name="Mail Sunucusu IP 5", null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Kullanıcı Adı", null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name="Şifre", null=True, blank=True)
    paymentType = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.MONTHLY, verbose_name="Ödeme Tipi"
    )
    priceUsd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ücret (USD)", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Sunucunun aktif/pasif durumunu belirtir.")
    isDefault = models.BooleanField(default=False, verbose_name="Varsayılan",
                                    help_text="Bu sunucunun varsayılan olup olmadığını belirtir.")

    class Meta:
        verbose_name = "S-Mail Sunucusu"
        verbose_name_plural = "S-Mail Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} Mail Sunucusu"


# DNS sunucularımızı buraya tınımlıyoruz
class DnsServer(AbstractBaseModel):
    operatingSystem = models.ForeignKey(
        OperatingSystem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşletim Sistemi"
    )
    domain = models.CharField(max_length=255, verbose_name="Domain", null=True, blank=True)
    ns1 = models.CharField(max_length=255, verbose_name="NS1", null=True, blank=True)
    ns2 = models.CharField(max_length=255, verbose_name="NS2", null=True, blank=True)
    ipAddress1 = models.GenericIPAddressField(verbose_name="DNS Sunucusu IP 1", null=True, blank=True)
    ipAddress2 = models.GenericIPAddressField(verbose_name="DNS Sunucusu IP 2", null=True, blank=True)
    ipAddress3 = models.GenericIPAddressField(verbose_name="DNS Sunucusu IP 3", null=True, blank=True)
    ipAddress4 = models.GenericIPAddressField(verbose_name="DNS Sunucusu IP 4", null=True, blank=True)
    ipAddress5 = models.GenericIPAddressField(verbose_name="DNS Sunucusu IP 5", null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Kullanıcı Adı", null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name="Şifre", null=True, blank=True)
    paymentType = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.MONTHLY, verbose_name="Ödeme Tipi"
    )
    priceUsd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ücret (USD)", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Sunucunun aktif/pasif durumunu belirtir.")
    isDefault = models.BooleanField(default=False, verbose_name="Varsayılan",
                                    help_text="Bu sunucunun varsayılan olup olmadığını belirtir.")

    class Meta:
        verbose_name = "S-DNS Sunucusu"
        verbose_name_plural = "S-DNS Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} DNS Sunucusu"


# site sunucu eşleşmelerei burada yapılıyor
class CustomSiteConfiguration(AbstractBaseModel):
    webServer = models.ForeignKey(
        WebServer,
        on_delete=models.CASCADE,
        related_name="webserver_configurations",
        verbose_name="Web Server",
        null=True,
        blank=True
    )
    sqlServer = models.ForeignKey(
        SqlServer,
        on_delete=models.CASCADE,
        related_name="sqlserver_configurations",
        verbose_name="SQL Server",
        null=True,
        blank=True
    )
    mailServer = models.ForeignKey(
        MailServer,
        on_delete=models.CASCADE,
        related_name="mailserver_configurations",
        verbose_name="Mail Server",
        null=True,
        blank=True
    )
    dnsServer = models.ForeignKey(
        DnsServer,
        on_delete=models.CASCADE,
        related_name="dnsserver_configurations",
        verbose_name="DNS Server",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Site Konfigürasyonu"
        verbose_name_plural = "Site Konfigürasyonları"

    def __str__(self):
        return f"{self.site.name} Konfigürasyonu"


# middleware ile ip kontrolü
class Blacklist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, default="Şüpheli davranış")
    is_active = models.BooleanField(default=True)

    # createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return f"{self.ip_address} - {self.reason} - {'Aktif' if self.is_active else 'Pasif'}"
