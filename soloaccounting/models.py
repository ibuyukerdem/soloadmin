from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models


class CustomUser(AbstractUser):
    phoneNumber = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefon Numarası')
    mobilePhone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Mobil Telefon')
    address = models.TextField(blank=True, null=True, verbose_name='Adres')
    postalCode = models.CharField(max_length=20, blank=True, null=True, verbose_name='Posta Kodu')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Şehir')
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name='İlçe')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ülke')
    dateOfBirth = models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')
    profilePicture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name='Profil Resmi')
    isIndividual = models.BooleanField(default=True, verbose_name='Kurumsal Fatura İstiyorum')
    identificationNumber = models.CharField(max_length=20, blank=True, null=True, verbose_name='TC Kimlik/Vergi Numarası')
    taxOffice = models.CharField(max_length=100, blank=True, null=True, verbose_name='Vergi Dairesi')
    companyName = models.CharField(max_length=255, blank=True, null=True, verbose_name='Şirket/Kuruluş Adı')
    isEfatura = models.BooleanField(default=False, verbose_name='e-Fatura Mükellefi')
    secretQuestion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Gizli Soru')
    secretAnswer = models.CharField(max_length=255, blank=True, null=True, verbose_name='Gizli Cevap')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Site')
    smsPermission = models.BooleanField(default=False, verbose_name='SMS İzni')
    digitalMarketingPermission = models.BooleanField(default=False, verbose_name='Dijital Pazarlama İzni')
    kvkkPermission = models.BooleanField(default=False, verbose_name='KVKK İzni')

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


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Ürün Adı", help_text="Ürün adını belirtiniz.")
    description = models.TextField(null=True, blank=True, verbose_name="Ürün Açıklaması",
                                   help_text="Ürün ile ilgili açıklama.")
    serviceDuration = models.PositiveIntegerField(verbose_name="Hizmet Süresi (Ay)",
                                                  help_text="Hizmet süresi ay cinsinden belirtilmelidir.")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ürün Fiyatı",
                                help_text="Ürün fiyatını belirtiniz.")
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Ürünün aktif/pasif durumunu belirtir.")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def __str__(self):
        return self.name


# bu tablo yazılımların modüllerini oluşturmalı
class Module(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modules',
        verbose_name="Ürün",
        help_text="Bu modüle ait bir ürün seçin (isteğe bağlı)."
    )
    name = models.CharField(max_length=255, unique=True, verbose_name="Modül Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Modül Açıklaması")
    serviceDuration = models.PositiveIntegerField(verbose_name="Hizmet Süresi (Ay)",
                                                  help_text="Hizmet süresi ay cinsinden belirtilmelidir.")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat",
                                help_text="Modül fiyatını belirtiniz.")
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Modülün aktif/pasif durumunu belirtir.")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Modül"
        verbose_name_plural = "Modüller"

    def __str__(self):
        return self.name


# bu tabloya web tasarımı, teknik destek, hosting gibi hizmetler eklenebilir
class Service(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name="Ürün",
        help_text="Bu hizmete ait bir ürün seçin (isteğe bağlı)."
    )
    name = models.CharField(max_length=255, verbose_name="Hizmet Adı", help_text="Hizmetin adını belirtiniz.")
    description = models.TextField(null=True, blank=True, verbose_name="Hizmet Açıklaması",
                                   help_text="Hizmet ile ilgili açıklama.")
    serviceDuration = models.PositiveIntegerField(verbose_name="Hizmet Süresi (Ay)",
                                                  help_text="Hizmet süresi ay cinsinden belirtilmelidir.")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Hizmet Fiyatı",
                                help_text="Hizmet fiyatını belirtiniz.")
    isActive = models.BooleanField(default=True, verbose_name="Aktif",
                                   help_text="Hizmetin aktif/pasif durumunu belirtir.")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"

    def __str__(self):
        return self.name


class SiteUrun(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name="module", verbose_name="Site")
    urun = models.ManyToManyField(Product, related_name="siteUrun", verbose_name="Ürünler")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Site Ürün Eşleşmesi"
        verbose_name_plural = "Site Ürün Eşleşmeleri"

    def __str__(self):
        return f"{self.site.name} - {', '.join([urun.name for urun in self.urun.all()])}"


class UserSite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userSites",
                             verbose_name="Kullanıcı")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="userSites", verbose_name="Site")
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Kullanıcı-Site İlişkisi"
        verbose_name_plural = "Kullanıcı-Site İlişkileri"

    def __str__(self):
        return f"{self.user.username} - {self.site.name}"


from django.db import models
from django.contrib.sites.models import Site


class OperatingSystem(models.Model):
    name = models.CharField(max_length=100, verbose_name="İşletim Sistemi Adı")
    version = models.CharField(max_length=50, verbose_name="Versiyon", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "S-İşletim Sistemi"
        verbose_name_plural = "S-İşletim Sistemleri"

    def __str__(self):
        return f"{self.name} {self.version}"


class PaymentType(models.TextChoices):
    MONTHLY = "Monthly", "Aylık"
    YEARLY = "Yearly", "Yıllık"


class WebServer(models.Model):
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
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "S-Web Sunucusu"
        verbose_name_plural = "S-Web Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} Web Sunucusu"


class SqlServer(models.Model):
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
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "S-SQL Sunucusu"
        verbose_name_plural = "S-SQL Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} SQL Sunucusu"


class MailServer(models.Model):
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
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "S-Mail Sunucusu"
        verbose_name_plural = "S-Mail Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} Mail Sunucusu"


class DnsServer(models.Model):
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
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "S-DNS Sunucusu"
        verbose_name_plural = "S-DNS Sunucuları"

    def __str__(self):
        return f"{self.domain} - {self.ipAddress1} DNS Sunucusu"


class CustomSiteConfiguration(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="configuration",
        verbose_name="Site"
    )
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

    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Site Konfigürasyonu"
        verbose_name_plural = "Site Konfigürasyonları"

    def __str__(self):
        return f"{self.site.name} Konfigürasyonu"

class Blacklist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, default="Şüpheli davranış")
    is_active = models.BooleanField(default=True)
    #createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return f"{self.ip_address} - {self.reason} - {'Aktif' if self.is_active else 'Pasif'}"