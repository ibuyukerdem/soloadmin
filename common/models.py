import hashlib
from zoneinfo import available_timezones

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import JSONField

from .utils.hash_key_manager import HashKeyManager


# -----------------------------------------------------------------------------
# common/models.py
# -----------------------------------------------------------------------------
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
    createdAt = models.DateTimeField(
        auto_now_add=True,
        help_text="Oluşturulma tarihi"
    )
    updatedAt = models.DateTimeField(
        auto_now=True,
        help_text="Son güncelleme tarihi"
    )

    class Meta:
        abstract = True


class LogEntry(models.Model):
    """
    İşlem loglarını saklayan model.
    """
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="log_entries",
        help_text="Logun ait olduğu site"
    )
    user = models.CharField(
        max_length=150,
        null=True, blank=True,
        help_text="İşlemi yapan kullanıcı"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="Kullanıcının IP adresi"
    )
    browser = models.CharField(
        max_length=150,
        null=True, blank=True,
        help_text="Kullanıcının tarayıcısı"
    )
    operating_system = models.CharField(
        max_length=150,
        null=True, blank=True,
        help_text="Kullanıcının işletim sistemi"
    )
    model_name = models.CharField(
        max_length=150,
        help_text="İşlem yapılan model"
    )
    operation = models.CharField(
        max_length=50,
        help_text="Yapılan işlem (CREATE, UPDATE, DELETE, vb.)"
    )
    hashed_data = models.TextField(
        null=True, blank=True,
        help_text="Hash'lenmiş işlem verisi"
    )
    previous_hashed_data = models.TextField(
        null=True, blank=True,
        help_text="Bir önceki kaydın hash'lenmiş verisi"
    )
    original_data = models.JSONField(
        null=True, blank=True,
        help_text="Orijinal veri"
    )
    status = models.CharField(
        max_length=50,
        default='Başarılı',
        help_text="İşlem durumu"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="İşlem zamanı"
    )

    def save(self, *args, **kwargs):
        """
        Hash zincirini oluştur ve kaydet.
        """
        # Bir önceki kaydı al (en yeni logu zaman sırasına göre çek).
        previous_log = LogEntry.objects.filter(site=self.site).order_by('-timestamp').first()
        self.previous_hashed_data = previous_log.hashed_data if previous_log else None

        # Dinamik anahtar oluştur.
        current_key = HashKeyManager.get_key_for_timestamp(self.timestamp)

        # Hash giriş verisini hazırla.
        hash_input = {
            "site": self.site.id,
            "user": self.user,
            "ip_address": self.ip_address,
            "browser": self.browser,
            "operating_system": self.operating_system,
            "model_name": self.model_name,
            "operation": self.operation,
            "previous_hashed_data": self.previous_hashed_data,
            "original_data": self.original_data,
            "timestamp": str(self.timestamp),
            "current_key": current_key,  # Anahtar dahil edilir
        }

        # Hash işlemini gerçekleştir.
        self.hashed_data = self.hash_data(hash_input)

        super().save(*args, **kwargs)

    @staticmethod
    def hash_data(data):
        """
        Veriyi hash'lemek için yardımcı fonksiyon.
        """
        if data:
            # Hash girdisini sıralı bir string haline getir.
            hash_input_string = str(sorted(data.items()))
            return hashlib.sha256(hash_input_string.encode('utf-8')).hexdigest()
        return None


class WhatsAppSettings(AbstractBaseModel):
    apiUrl = models.URLField(
        max_length=500,
        verbose_name="WhatsApp API URL"
    )
    phoneNumber = models.CharField(
        max_length=20,
        verbose_name="Telefon Numarası"
    )
    apiKey = models.CharField(
        max_length=255,
        verbose_name="API Anahtarı"
    )
    kontorMiktari = models.PositiveIntegerField(
        verbose_name="Kontör Miktarı",
        default=0
    )

    class Meta:
        verbose_name = "WhatsApp Ayarı"
        verbose_name_plural = "A-WhatsApp Ayarları"
        db_table = "whatsapp_settings"

    def __str__(self):
        return f"{self.site.domain} WhatsApp Ayarları"


class SmsSettings(AbstractBaseModel):
    url = models.URLField(
        max_length=500,
        verbose_name="SMS API URL"
    )
    username = models.CharField(
        max_length=255,
        verbose_name="Kullanıcı Adı"
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Şifre"
    )
    kontorMiktari = models.PositiveIntegerField(
        verbose_name="Kontör Miktarı",
        default=0
    )

    class Meta:
        verbose_name = "SMS Ayarı"
        verbose_name_plural = "A-SMS Ayarları"
        db_table = "sms_settings"

    def __str__(self):
        return f"{self.site.domain} SMS Ayarları"


class SmtpSettings(AbstractBaseModel):
    emailAddress = models.EmailField(
        max_length=255,
        verbose_name="Gönderici E-posta Adresi"
    )
    smtpServer = models.CharField(
        max_length=255,
        verbose_name="SMTP Sunucusu"
    )
    smtpPort = models.PositiveIntegerField(
        verbose_name="SMTP Portu",
        default=587
    )
    username = models.CharField(
        max_length=255,
        verbose_name="Kullanıcı Adı"
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Şifre"
    )
    useTls = models.BooleanField(
        default=True,
        verbose_name="TLS Kullanımı"
    )
    useSsl = models.BooleanField(
        default=False,
        verbose_name="SSL Kullanımı"
    )

    class Meta:
        verbose_name = "SMTP Ayarı"
        verbose_name_plural = "A-SMTP Ayarları"
        db_table = "smtp_settings"

    def __str__(self):
        return f"{self.site.domain} SMTP Ayarları"


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
        # Django'nun Site modelinde 'name' alanı bulunur, domain de kullanılabilir.
        return f"{self.get_applicationType_display()} - {self.site.name}"

    class Meta:
        verbose_name = "Google Uygulama Entegrasyonu"
        verbose_name_plural = "Google Uygulama Entegrasyonları"


class SiteSettings(AbstractBaseModel):
    """
    Site ile ilgili temel ayarları ve meta bilgileri tutar.
    """

    # -- Temel Site Bilgileri --
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

    # -- Logo & Favicon --
    faviconBlack = models.ImageField(
        upload_to="favicon/",
        null=True, blank=True,
        verbose_name="Siyah Favicon",
        help_text="Siyah arka plan favicon yükleyin."
    )
    faviconWhite = models.ImageField(
        upload_to="favicon/",
        null=True, blank=True,
        verbose_name="Beyaz Favicon",
        help_text="Beyaz arka plan favicon yükleyin."
    )
    logoBlack = models.ImageField(
        upload_to="logos/",
        null=True, blank=True,
        verbose_name="Siyah Logo",
        help_text="Siyah arka plan logo yükleyin."
    )
    logoWhite = models.ImageField(
        upload_to="logos/",
        null=True, blank=True,
        verbose_name="Beyaz Logo",
        help_text="Beyaz arka plan logo yükleyin."
    )

    # -- Renkler & Font --
    colors = JSONField(
        default=list,
        verbose_name="Site Renkleri",
        help_text="Site için kullanılacak ana renk kodlarının listesi (max 4)."
    )
    googleFont = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Google Font",
        help_text="Google Fonts üzerinde tanımlı font ismini giriniz."
    )

    # -- Tema Seçenekleri --
    HOME_THEME_CHOICES = (
        (1, "Tema 1"),
        (2, "Tema 2"),
        (3, "Tema 3"),
    )
    CATEGORY_THEME_CHOICES = (
        (1, "Tema 1"),
        (2, "Tema 2"),
    )
    ARTICLE_DETAIL_THEME_CHOICES = (
        (1, "Tema 1"),
        (2, "Tema 2"),
    )
    homeTheme = models.PositiveSmallIntegerField(
        choices=HOME_THEME_CHOICES,
        default=1,
        verbose_name="Anasayfa Teması",
        help_text="Anasayfa için tema seçiniz (1,2,3)."
    )
    categoryTheme = models.PositiveSmallIntegerField(
        choices=CATEGORY_THEME_CHOICES,
        default=1,
        verbose_name="Kategori Teması",
        help_text="Kategoriler için tema seçiniz (1,2)."
    )
    articleDetailTheme = models.PositiveSmallIntegerField(
        choices=ARTICLE_DETAIL_THEME_CHOICES,
        default=1,
        verbose_name="Makale Detay Teması",
        help_text="Makale detay sayfası için tema seçiniz (1,2)."
    )

    # -- Politikalar --
    cookiePolicy = models.TextField(
        null=True, blank=True,
        verbose_name="Çerez Politikası",
        help_text="Sitenin çerez politikasını burada belirtin."
    )
    privacyPolicy = models.TextField(
        null=True, blank=True,
        verbose_name="Gizlilik Politikası",
        help_text="Sitenin gizlilik politikasını burada belirtin."
    )
    termsOfUse = models.TextField(
        null=True, blank=True,
        verbose_name="Kullanım Koşulları",
        help_text="Sitenin kullanım koşullarını burada belirtin."
    )
    kvkkAgreement = models.TextField(
        null=True, blank=True,
        verbose_name="KVKK Aydınlatma Metni",
        help_text="KVKK ile ilgili sözleşme veya aydınlatma metnini belirtin."
    )

    # -- İletişim --
    phone = models.CharField(
        max_length=15,
        null=True, blank=True,
        verbose_name="Telefon",
        help_text="İletişim için sabit telefon numarasını girin."
    )
    gsm = models.CharField(
        max_length=15,
        null=True, blank=True,
        verbose_name="GSM",
        help_text="İletişim için mobil telefon numarasını girin."
    )
    email = models.EmailField(
        null=True, blank=True,
        verbose_name="E-posta",
        help_text="İletişim için e-posta adresini girin."
    )
    address = models.TextField(
        null=True, blank=True,
        verbose_name="Adres",
        help_text="İletişim için adres bilgilerini girin."
    )
    googleMap = models.URLField(
        null=True, blank=True,
        verbose_name="Google Harita",
        help_text="Google Haritalar linkini girin."
    )

    # -- Hakkımızda --
    aboutUsTitle = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Hakkımızda Başlık",
        help_text="Hakkımızda sayfası için başlık."
    )
    aboutUsContent = models.TextField(
        null=True, blank=True,
        verbose_name="Hakkımızda İçerik",
        help_text="Hakkımızda sayfası metni."
    )
    aboutUsImage = models.ImageField(
        upload_to="about_us/",
        null=True, blank=True,
        verbose_name="Hakkımızda Görsel",
        help_text="Hakkımızda sayfası için görsel yükleyin."
    )

    def __str__(self):
        return f"{self.siteName} ({self.site.domain})"

    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"


class SocialMedia(AbstractBaseModel):
    """
    Maksimum 7 adet sosyal medya ikonu/linki.
    Burada kod düzeyinde kontrol sağlanabilir (admin veya serializer tarafında).
    """
    icon = models.CharField(
        max_length=50,
        verbose_name="Sosyal Medya İkon Kodu",
        help_text="Font Awesome veya benzeri ikon class ismi."
    )
    link = models.URLField(
        verbose_name="Sosyal Medya Linki",
        help_text="Sosyal medyanın tam URL adresini belirtin."
    )

    def __str__(self):
        return f"{self.icon} - {self.link}"

    class Meta:
        verbose_name = "Sosyal Medya"
        verbose_name_plural = "Sosyal Medyalar"


class HomePageSettings(AbstractBaseModel):
    """
    Anasayfa özel alanları tutulur.
    - Giriş Slider
    - Son Makaleler Slogan
    - Kayan Yazı
    - Alt Bilgi Duyuru
    """
    # Giriş Slider
    sliderSlogan = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Slider Slogan",
        help_text="Giriş slider'ında üst kısımda yer alan slogan."
    )
    sliderSubText = models.TextField(
        null=True, blank=True,
        verbose_name="Slider Alt Bilgi",
        help_text="Giriş slider'ında açıklama/alt bilgi metni."
    )
    sliderButtonText = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name="Slider Alt Bilgi Buton İsmi",
        help_text="Slider üzerinde görünecek butonun metni."
    )
    sliderButtonLink = models.URLField(
        null=True, blank=True,
        verbose_name="Slider Alt Bilgi Buton Linki",
        help_text="Butona tıklandığında gidilecek link."
    )

    # Son Makaleler
    lastArticlesSlogan = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Son Makaleler Slogan",
        help_text="Anasayfadaki son makaleler için slogan başlık."
    )

    # Kayan Yazı
    tickerText = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Kayan Yazı Metni",
        help_text="Anasayfada kayan uyarı/metin."
    )

    # Alt Bilgi Duyuru
    footerAnnouncementTitle = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Başlık",
        help_text="Footer üzerinde duyuru başlığı."
    )
    footerAnnouncementButtonText = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Buton İsmi",
        help_text="Duyuru altındaki butonun metni."
    )
    footerAnnouncementButtonLink = models.URLField(
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Buton Linki",
        help_text="Duyuru butonuna tıklayınca gidilecek link."
    )

    def __str__(self):
        return f"Anasayfa Ayarları - Site ID: {self.site_id}"

    class Meta:
        verbose_name = "Anasayfa Ayarları"
        verbose_name_plural = "Anasayfa Ayarları"


class FooterSettings(AbstractBaseModel):
    """
    Alt bilgi (footer) alanındaki slogan, duyuru ve yardımcı linkler vb. saklanır.
    """
    footerSlogan = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Alt Bilgi Slogan",
        help_text="Footer'da yer alan kısa slogan."
    )

    # Alt Bilgi Duyuru
    footerAnnouncementTitle = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Başlık"
    )
    footerAnnouncementButtonText = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Buton İsmi"
    )
    footerAnnouncementButtonLink = models.URLField(
        null=True, blank=True,
        verbose_name="Alt Bilgi Duyuru Buton Linki"
    )

    # Yardımcı Linkler (JSON)
    helperLinks = JSONField(
        default=list,
        verbose_name="Yardımcı Linkler",
        help_text="Footer alanında gösterilecek linklerin listesi (İsim/URL)."
    )

    # Alt Alan Bilgi (Footer en alt yazı)
    footerBottomText = models.TextField(
        null=True, blank=True,
        verbose_name="Alt Alan Bilgi",
        help_text="Footer'ın en alt kısmında yer alan metin, copyright vb."
    )

    def __str__(self):
        return f"Footer Ayarları - Site ID: {self.site_id}"

    class Meta:
        verbose_name = "Footer Ayarları"
        verbose_name_plural = "Footer Ayarları"


class Menu(AbstractBaseModel):
    """
    Sitedeki menü yapısını tutar. Ana menüde en fazla 6 adet olabilir (kod tarafında kontrol).
    - Öne çıkan menü mü?
    - Kategoriler gözüksün mü?
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Menü Başlık",
        help_text="Menüde görünecek başlık."
    )
    link = models.CharField(
        max_length=255,
        verbose_name="Menü Linki",
        help_text="Menüye tıklandığında gidilecek URL veya route."
    )
    isMainMenu = models.BooleanField(
        default=False,
        verbose_name="Ana Menü",
        help_text="Bu menü ana menüde mi gösterilsin?"
    )
    isFeatured = models.BooleanField(
        default=False,
        verbose_name="Öne Çıkan Gözüksün mü?",
        help_text="Menüyü öne çıkarılmış gibi göster."
    )
    showCategories = models.BooleanField(
        default=False,
        verbose_name="Kategoriler Gözüksün mü?",
        help_text="Bu menü altında kategoriler otomatik listelensin mi?"
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Sıralama",
        help_text="Menünün görüntüleneceği sıralama değeri."
    )

    def __str__(self):
        return f"{self.title} (MainMenu={self.isMainMenu})"

    class Meta:
        verbose_name = "Menü"
        verbose_name_plural = "Menüler"


# -----------------------------------------------------------------------------
# CustomUser (common/models.py)
# -----------------------------------------------------------------------------
class CustomUser(AbstractUser):
    phoneNumber = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Telefon Numarası'
    )
    mobilePhone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Mobil Telefon'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Adres'
    )
    postalCode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Posta Kodu'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Şehir'
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='İlçe'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ülke'
    )
    dateOfBirth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Doğum Tarihi'
    )
    profilePicture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Profil Resmi'
    )
    isIndividual = models.BooleanField(
        default=False,
        verbose_name='Kurumsal Fatura İstiyorum'
    )
    identificationNumber = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='TC Kimlik/Vergi Numarası'
    )
    taxOffice = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Vergi Dairesi'
    )
    companyName = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Şirket/Kuruluş Adı'
    )
    isEfatura = models.BooleanField(
        default=False,
        verbose_name='e-Fatura Mükellefi'
    )
    secretQuestion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Gizli Soru'
    )
    secretAnswer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Gizli Cevap'
    )
    smsPermission = models.BooleanField(
        default=False,
        verbose_name='SMS İzni'
    )
    digitalMarketingPermission = models.BooleanField(
        default=False,
        verbose_name='Dijital Pazarlama İzni'
    )
    kvkkPermission = models.BooleanField(
        default=False,
        verbose_name='KVKK İzni'
    )
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in sorted(available_timezones())],
        default="Europe/Istanbul",
        verbose_name="Saat Dilimi"
    )
    preferred_language = models.CharField(
        max_length=10,
        default="en",
        choices=[
            ('en', 'English'),
            ('tr', 'Türkçe'),
            ('de', 'Deutsch'),
            ('fr', 'Français'),
            ('nl', 'Nederlands'),
            ('ar', 'العربية'),
        ],
        verbose_name="Tercih Edilen Dil"
    )
    selectedSite = models.ForeignKey(
        Site,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Aktif Seçilen Site"
    )
    dealerID = models.ForeignKey(
        'self',  # Modelin kendisine referans
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'isDealer': True},  # Sadece isDealer=True olanlar
        verbose_name='Bayi'
    )
    dealer_segment = models.ForeignKey(
        'soloaccounting.DealerSegment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Bayi Segmenti",
        default=None
    )
    isDealer = models.BooleanField(
        default=False,
        verbose_name='Bayi Mi?'
    )  # Bayi olup olmadığını belirtir
    discountRate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='İskonto Oranı'
    )  # İskonto oranı (ör. 5.25% gibi)

    # Aşağıdaki alanlar, CustomUser ile group ve permission yönetimini sağlar.
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='CustomUser_groups',
        blank=True,
        verbose_name='Gruplar'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='CustomUser_permissions',
        blank=True,
        verbose_name='Kullanıcı İzinleri'
    )

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return self.username
