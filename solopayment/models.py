"""
Bu dosya, e-tahsilat (e-collection) sisteminizde kullanılacak temel modelleri içerir.

1) AbstractBaseModel:
   - Tüm modeller için ortak 'site' alanını ve
     oluşturulma/güncellenme zaman damgasını içeren soyut bir modeldir.

2) PaymentProvider:
   - Sipay, PayTR, Halkbank, Garanti vb. gibi tüm sitelerde ortak kullanılabilen
     ödeme sağlayıcı bilgilerini saklar.
   - 'createDate' ve 'updateDate' alanlarıyla kayıt zamanlarını tutar.

3) PaymentMethod:
   - Bir işletme/merchant (AUTH_USER_MODEL) ile bir PaymentProvider arasındaki ilişkiyi tanımlar.
   - API kimlik bilgileri (credentials), komisyonu kimin ödediği vb. bilgileri barındırır.
   - AbstractBaseModel'i miras alır; her kaydın hangi siteye ait olduğu kayıtlıdır.

4) PaymentFee:
   - PaymentMethod bazında; taksit veya peşin işlemlerde sabit/ yüzdesel komisyon, vade farkı gibi
     ek ücret tanımlarını tutar.
   - AbstractBaseModel'i miras alır.

5) PaymentTransaction:
   - Gerçekleşen ödeme işlemlerini kaydeder.
   - Ödemeyi alan işletme (merchantUser) ile ödeyen kullanıcıyı (payingUser) veya 'guest' ödemeyi
     (payerName, payerNote) ilişkilendirir.
   - AbstractBaseModel'i miras alır.
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models

from common.models import AbstractBaseModel


# ------------------------------------------------------------------------
# 1) PaymentProvider (Tüm siteler için ortak)
# ------------------------------------------------------------------------
class PaymentProvider(models.Model):
    """
    Tüm sitelerde ortak kullanılabilecek ödeme sağlayıcılarını tutan model.
    Örnek: Sipay, PayTR, Halkbank, Garanti vb.

    createDate ve updateDate alanlarıyla kayıt zaman bilgisi tutulur.
    site ile ilişkisi yoktur; tüm sistemde ortak kullanılır.
    """
    providerName = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Sağlayıcı Adı"
    )
    providerCode = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Kısa Kod"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Açıklama"
    )
    isActive = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?"
    )

    # Kayıt zaman alanları (site ile ilişki yok!)
    createDate = models.DateTimeField(
        auto_now_add=True,
        help_text="Kayıt oluşturulma tarihi/saatini belirtir."
    )
    updateDate = models.DateTimeField(
        auto_now=True,
        help_text="Kayıt son güncelleme tarihi/saatini belirtir."
    )

    class Meta:
        verbose_name = "Ödeme Sağlayıcısı"
        verbose_name_plural = "Ödeme Sağlayıcıları"

    def __str__(self):
        return self.providerName


# ------------------------------------------------------------------------
# 2) PaymentMethod (Site bazlı, merchant'a özel ayarlar)
# ------------------------------------------------------------------------
class PaymentMethod(AbstractBaseModel):
    """
    Bir müşterinin (merchantUser) bir ödeme sağlayıcısını hangi ayarlarla
    kullandığını tanımlayan model.
    AbstractBaseModel'i miras aldığı için:
      - site (ForeignKey)
      - createdAt, updatedAt
    alanları otomatik eklenir.
    """
    merchantUser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paymentMethods",
        verbose_name="İşletme Sahibi"
    )
    paymentProvider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="paymentMethods",
        verbose_name="Ödeme Sağlayıcısı"
    )
    defaultForSingleShot = models.BooleanField(
        default=False,
        verbose_name="Tek Çekim Varsayılanı"
    )
    COMMISSION_PAYER_CHOICES = (
        ("merchant", "Komisyonu İşletme Öder"),
        ("customer", "Komisyonu Müşteri Öder"),
    )
    commissionPayer = models.CharField(
        max_length=10,
        choices=COMMISSION_PAYER_CHOICES,
        default="merchant",
        verbose_name="Komisyon Ödeyici"
    )
    isActive = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?"
    )
    credentials = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Ek Parametreler / API Bilgileri"
    )

    class Meta:
        verbose_name = "Ödeme Yöntemi"
        verbose_name_plural = "Ödeme Yöntemleri"

    def __str__(self):
        return f"{self.merchantUser} - {self.paymentProvider.providerName}"


# ------------------------------------------------------------------------
# 3) PaymentFee (Site bazlı, PaymentMethod'a ait komisyon/vade tanımları)
# ------------------------------------------------------------------------
class PaymentFee(AbstractBaseModel):
    """
    Peşin veya taksitli işlemler için sabit veya oransal komisyon/vade farkı tanımları.
    AbstractBaseModel'i miras aldığı için:
      - site (ForeignKey)
      - createdAt, updatedAt
    alanları otomatik eklenir.
    """
    paymentMethod = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="fees",
        verbose_name="Ödeme Yöntemi"
    )
    installmentCount = models.PositiveIntegerField(
        default=1,
        verbose_name="Taksit Sayısı"
    )
    fixedFee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Sabit Ücret"
    )
    percentageFee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Oransal Ücret (%)"
    )
    isActive = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?"
    )

    class Meta:
        verbose_name = "Komisyon/Vade Tanımı"
        verbose_name_plural = "Komisyon/Vade Tanımları"
        unique_together = ("paymentMethod", "installmentCount")

    def __str__(self):
        return (
            f"{self.paymentMethod.paymentProvider.providerName} | "
            f"{self.installmentCount} Taksit | "
            f"Fix={self.fixedFee}, %{self.percentageFee}"
        )


# ------------------------------------------------------------------------
# 4) PaymentTransaction (Site bazlı, gerçekleşen ödemelerin kaydı)
# ------------------------------------------------------------------------
class PaymentTransaction(AbstractBaseModel):
    """
    Gerçekleşen ödeme işlemlerinin kayıtlarını tutar.
    AbstractBaseModel'i miras aldığı için:
      - site (ForeignKey)
      - createdAt, updatedAt
    alanları otomatik eklenir.

    Örneğin:
      - merchantUser: Ödemeyi alan işletme sahibi
      - payingUser: Ödeyen kullanıcı (login) veya None (guest)
      - payerName, payerNote: Guest ise burada kaydedilebilir
    """
    merchantUser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paymentTransactions",
        verbose_name="İşletme Sahibi"
    )
    payingUser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="paidTransactions",
        blank=True,
        null=True,
        verbose_name="Ödemeyi Yapan Kullanıcı (Girişli)"
    )
    payerName = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ödeyen Adı (Guest)"
    )
    payerNote = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ödeme Notu (Guest)"
    )
    paymentMethod = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Ödeme Yöntemi"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Ödenecek Tutar"
    )
    installmentCount = models.PositiveIntegerField(
        default=1,
        verbose_name="Taksit Sayısı"
    )
    totalPaidAmount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Toplam Ödenen Tutar"
    )
    STATUS_CHOICES = (
        ("pending", "Beklemede"),
        ("approved", "Onaylandı"),
        ("declined", "Reddedildi"),
        ("error", "Hata"),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="İşlem Durumu"
    )
    referenceCode = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Banka Referans Kodu"
    )
    calculatedFixedFee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Hesaplanan Sabit Ücret"
    )
    calculatedPercentageFee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Hesaplanan Oransal Ücret"
    )

    class Meta:
        verbose_name = "Ödeme İşlemi"
        verbose_name_plural = "Ödeme İşlemleri"

    def __str__(self):
        return (
            f"Txn#{self.pk} | {self.merchantUser} | "
            f"{self.paymentMethod.paymentProvider.providerName} | {self.amount} TL"
        )
