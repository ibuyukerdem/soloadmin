#soloaccounting/servers/models.py
from django.db import models
from common.models import AbstractBaseModel
###################server tanımlama tabloları ##################

class PaymentType(models.TextChoices):
    MONTHLY = "Monthly", "Aylık"
    YEARLY = "Yearly", "Yıllık"

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

##########################################################
