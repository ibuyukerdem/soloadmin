from django.db import models
from django.contrib.sites.models import Site

class AbstractBaseModel(models.Model):
    """
    Tüm modellerde tekrar eden site bağlantısını ve
    oluşturulma/güncelleme tarihlerini tutan soyut model.
    """
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        help_text="Bu kaydın ait olduğu siteyi belirtir."
    )
    createdAt = models.DateTimeField(auto_now_add=True, help_text="Oluşturulma tarihi")
    updatedAt = models.DateTimeField(auto_now=True, help_text="Son güncelleme tarihi")

    class Meta:
        abstract = True

class GoogleApplicationsIntegration(AbstractBaseModel):
    """
    Google Webmasters, Analytics, Tag Manager, Adsense gibi Google uygulamaları için
    seçimli sütun ve bu uygulamalara ait kodların saklanacağı model.
    """
    APPLICATION_CHOICES = [
        ("google_webmasters", "Google Webmasters"),
        ("google_analytics", "Google Analytics"),
        ("google_tag_manager", "Google Tag Manager"),
        ("google_adsense", "Google Adsense"),
    ]

    applicationType = models.CharField(
        max_length=50,
        choices=APPLICATION_CHOICES,
        verbose_name="Uygulama Türü",
        help_text="Google uygulama türünü belirtir (ör. Google Analytics, Tag Manager, Adsense)."
    )
    applicationCode = models.TextField(
        verbose_name="Uygulama Kodu",
        help_text="Google uygulaması tarafından sağlanan entegrasyon kodu."
    )

    def __str__(self):
        return f"{self.get_applicationType_display()} - {self.site.name}"

    class Meta:
        verbose_name = "Google Uygulama Entegrasyonu"
        verbose_name_plural = "Google Uygulama Entegrasyonları"


class SiteSettings(AbstractBaseModel):
    """
    Site ayarları için model. Siteye ait meta bilgileri, iletişim detayları ve
    sözleşme metinlerini tutar.
    """

    siteName = models.CharField(
        max_length=255,
        verbose_name="Site Adı",
        help_text="Sitenin görünen adını belirtin."
    )
    metaTitle = models.CharField(
        max_length=255,
        verbose_name="Meta Başlık",
        help_text="SEO için sitenin meta başlığını belirtin."
    )
    metaDescription = models.TextField(
        verbose_name="Meta Açıklama",
        help_text="SEO için sitenin meta açıklamasını belirtin."
    )
    logo = models.ImageField(
        upload_to="logos/",
        verbose_name="Logo",
        help_text="Site logosunu yükleyin."
    )
    cookiePolicy = models.TextField(
        verbose_name="Çerez Politikası",
        help_text="Sitenin çerez politikasını burada belirtin."
    )
    privacyPolicy = models.TextField(
        verbose_name="Gizlilik Politikası",
        help_text="Sitenin gizlilik politikasını burada belirtin."
    )
    termsOfUse = models.TextField(
        verbose_name="Kullanım Koşulları",
        help_text="Sitenin kullanım koşullarını burada belirtin."
    )
    phone = models.CharField(
        max_length=15,
        verbose_name="Telefon",
        help_text="İletişim için sabit telefon numarasını girin."
    )
    gsm = models.CharField(
        max_length=15,
        verbose_name="GSM",
        help_text="İletişim için mobil telefon numarasını girin."
    )
    email = models.EmailField(
        verbose_name="E-posta",
        help_text="İletişim için e-posta adresini girin."
    )
    address = models.TextField(
        verbose_name="Adres",
        help_text="İletişim için adres bilgilerini girin."
    )
    googleMap = models.URLField(
        verbose_name="Google Harita",
        help_text="Google Haritalar bağlantısını girin."
    )
    aboutUs = models.TextField(
        verbose_name="Hakkımızda",
        help_text="Sitenin hakkımızda metnini buraya yazın."
    )
    kvkkAgreement = models.TextField(
        verbose_name="KVKK Sözleşmesi",
        help_text="KVKK ile ilgili sözleşme metnini burada belirtin."
    )

    def __str__(self):
        return self.siteName

    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"
