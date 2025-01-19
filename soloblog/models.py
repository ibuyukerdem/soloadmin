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
from io import BytesIO

from PIL import Image as PILImage
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import F, Max
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from common.models import AbstractBaseModel

# Eğer Django 3.1+'sa JSONField'i kullanabilirsiniz:
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class Category(AbstractBaseModel):
    categoryName = models.CharField(max_length=255, verbose_name="Kategori Adı")
    categoryDescription = models.TextField(verbose_name="Kategori Açıklaması")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="URL Yolu")
    meta = models.TextField(blank=True, null=True, verbose_name="Meta Veriler")
    metaDescription = models.TextField(blank=True, null=True, verbose_name="Meta Açıklaması")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
        verbose_name="Üst Kategori"
    )
    order = models.IntegerField(default=0, verbose_name="Sıra")
    categoryImage = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True,
        verbose_name="Kategori Görseli"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        indexes = [
            models.Index(fields=["site"]),  # Site bazlı sorgular
        ]

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("Kategori kendi kendisinin ebeveyni olamaz.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                # Güncelleme işlemi
                old_category = Category.objects.get(pk=self.pk)
                old_order = old_category.order
                new_order = self.order
                if old_order != new_order:
                    if new_order < old_order:
                        Category.objects.filter(
                            site=self.site,
                            order__gte=new_order,
                            order__lt=old_order
                        ).exclude(pk=self.pk).update(order=F('order') + 1)
                    else:
                        Category.objects.filter(
                            site=self.site,
                            order__gt=old_order,
                            order__lte=new_order
                        ).exclude(pk=self.pk).update(order=F('order') - 1)
            else:
                # Yeni kayıt oluşturma işlemi
                if self.order == 0:
                    max_order = Category.objects.filter(site=self.site).aggregate(
                        Max('order')
                    ).get('order__max') or 0
                    self.order = max_order + 1
                else:
                    # Yeni kategori belirli bir sıraya eklenmek isteniyor
                    Category.objects.filter(
                        site=self.site,
                        order__gte=self.order
                    ).update(order=F('order') + 1)
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Alt kategoriler varsa silme
        if Category.objects.filter(parent=self).exists():
            raise ValidationError("Alt kategorileri olan bir kategori silinemez.")

        # Eğer bu kategoriye bağlı makaleler varsa silme
        if self.article_set.exists():
            raise ValidationError("Bu kategoriye bağlı makaleler olduğu için silinemez.")

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.categoryName}"


# Resim dosyasını silmek için post_delete sinyali
@receiver(post_delete, sender=Category)
def delete_category_image(sender, instance, **kwargs):
    if instance.categoryImage:
        instance.categoryImage.delete(False)


# Güncelleme sırasında eski resmi silmek için pre_save sinyali
@receiver(pre_save, sender=Category)
def delete_old_category_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Category.objects.get(pk=instance.pk)
            if old_instance.categoryImage and old_instance.categoryImage != instance.categoryImage:
                old_instance.categoryImage.delete(False)
        except Category.DoesNotExist:
            pass


# Article Model
class Article(AbstractBaseModel):
    """
    Makale modeli, AbstractBaseModel'i miras alır.
    """
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Kategori")
    title = models.CharField(max_length=255, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    slider = models.BooleanField(default=False, verbose_name="Slider Gösterimi")
    active = models.BooleanField(default=True, verbose_name="Aktif")
    slug = models.SlugField(max_length=255, verbose_name="URL Yolu")
    counter = models.IntegerField(default=0, verbose_name="Sayaç")
    meta = models.TextField(blank=True, null=True, verbose_name="Meta Veriler")
    metaDescription = models.TextField(blank=True, null=True, verbose_name="Meta Açıklaması")
    publicationDate = models.DateTimeField(auto_now_add=True, verbose_name="Yayınlanma Tarihi")
    image = models.ImageField(
        upload_to='article_images/',
        blank=True,
        null=True,
        verbose_name="Makale Resmi"
    )

    class Meta:
        verbose_name = "Makale"
        verbose_name_plural = "Makaleler"
        unique_together = ('site', 'slug')
        indexes = [
            models.Index(fields=["category"]),  # Kategori bazlı sorgular için
            models.Index(fields=["site"]),  # Site bazlı sorgular için
            models.Index(fields=["slug"]),  # Slug bazlı sorgular için
            models.Index(fields=["title"]),  # Başlığa göre aramalar için
            models.Index(fields=["publicationDate"]),  # Tarih sıralama ve sorguları için
            models.Index(fields=["site", "category"]),
        ]

    def save(self, *args, **kwargs):
        # Eğer slug boşsa title'dan otomatik oluştur
        if not self.slug:
            # allow_unicode=True diyerek UTF-8 desteğini etkinleştiriyoruz.
            self.slug = slugify(self.title, allow_unicode=True)

        # Eğer oluşan slug database'de varsa, sonuna sayı ekleyerek unique hale getirebilirsiniz.
        # Basit bir örnek:
        original_slug = self.slug
        counter = 1
        while Article.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"{self.slug}"


# Resim dosyasını silmek için post_delete sinyali
@receiver(post_delete, sender=Article)
def delete_article_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(False)


# Güncelleme sırasında eski resmi silmek için pre_save sinyali
@receiver(pre_save, sender=Article)
def delete_old_article_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            # Yeni resim ile eski resim farklı ise eskiyi sil
            if old_instance.image and old_instance.image != instance.image:
                old_instance.image.delete(False)
        except Article.DoesNotExist:
            pass


@receiver(post_delete, sender='soloblog.Article')
def delete_article_images(sender, instance, **kwargs):
    """
    Makale silindiğinde ilişkili resimleri ve dosyaları kaldırır.
    """
    from soloblog.models import Image  # Bağımlılığı doğrudan ilişkilendirmek için içe aktarım yapıldı.
    images = Image.objects.filter(article=instance)
    for image in images:
        if image.imagePath:
            image.imagePath.delete()
        if image.resizedImage:
            image.resizedImage.delete()


def get_image_upload_path(instance, filename):
    """
    Resimlerin yükleme yolunu belirler. Site ID ve makale slug'ı ile organize eder.
    """
    siteId = instance.article.site.id
    articleSlug = instance.article.slug
    base, ext = os.path.splitext(filename)
    newFilename = f"{articleSlug}_{base}{ext}"
    return f'images/site_{siteId}/{newFilename}'


class Image(AbstractBaseModel):
    """
    Resim modeli, makaleye ait resimlerin yüklenmesi ve yönetimi için kullanılır.
    """
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        verbose_name="Makale",
        related_name='images'
    )
    imagePath = models.ImageField(
        upload_to=get_image_upload_path,
        verbose_name="Resim Yolu"
    )
    resizedImage = models.ImageField(
        upload_to=get_image_upload_path,
        blank=True,
        null=True,
        verbose_name="Boyutlandırılmış Resim"
    )

    def save(self, *args, **kwargs):
        if self.imagePath:
            self.compress_original_image()
            if not self.resizedImage:
                self.create_resized_image()
        super().save(*args, **kwargs)

    def compress_original_image(self):
        # eğer field boşsa veya path özelliği yoksa => placeholder olabilir
        if not self.imagePath or not hasattr(self.imagePath, 'path'):
            return

        # eğer "http" ile başlıyorsa => yine placeholder
        if self.imagePath.name.startswith("http"):
            return
        """Orijinal resmi sıkıştırarak JPEG formatında kaydet ve orijinal dosyayı sil"""
        with PILImage.open(self.imagePath) as image:
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            output = BytesIO()
            image.save(output, format='JPEG', quality=75)  # Sıkıştırma kalitesini ayarlayabilirsiniz
            output.seek(0)
            originalPath = self.imagePath.path
            self.imagePath.save(self.get_filename('compressed', 'jpg'), ContentFile(output.read()), save=False)
            if os.path.exists(originalPath):
                os.remove(originalPath)

    def create_resized_image(self):
        # eğer URL ise atla
        if not self.imagePath or not hasattr(self.imagePath, 'path'):
            return
        if self.imagePath.name.startswith("http"):
            return
        """Resmi kare kırpıp WEBP formatında kaydet"""
        if not self.imagePath:
            return

        with PILImage.open(self.imagePath) as image:
            resizedSize = (543, 543)
            croppedImage = self.make_square(image, resizedSize)
            self.resizedImage.save(self.get_filename('resized', 'webp'), ContentFile(croppedImage.read()), save=False)

    def make_square(self, image, size):
        width, height = image.size
        newWidth, newHeight = size

        left = (width - newWidth) / 2
        top = (height - newHeight) / 2
        right = (width + newWidth) / 2
        bottom = (height + newHeight) / 2

        croppedImage = image.crop((left, top, right, bottom))

        if croppedImage.size[0] > size[0] or croppedImage.size[1] > size[1]:
            croppedImage.thumbnail(size, PILImage.LANCZOS)

        output = BytesIO()
        croppedImage.save(output, format='WEBP')
        output.seek(0)
        return output

    def get_filename(self, prefix, extension):
        return f"{prefix}_{self.pk}.{extension}"

    def delete(self, *args, **kwargs):
        if self.imagePath:
            self.imagePath.delete(save=False)
        if self.resizedImage:
            self.resizedImage.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Makale Resim"
        verbose_name_plural = "Makale Resimleri"

    def __str__(self):
        return self.imagePath.url


# Signal to delete the file when the record is deleted
@receiver(post_delete, sender=Image)
def delete_image_files(sender, instance, **kwargs):
    if instance.imagePath:
        instance.imagePath.delete(save=False)
    if instance.resizedImage:
        instance.resizedImage.delete(save=False)


# Comment Model
class Comment(AbstractBaseModel):
    """
    Yorum modeli, makalelere yapılan yorumları tutar.
    """
    article = models.ForeignKey('Article', on_delete=models.CASCADE, verbose_name="Makale", related_name="comments")
    approved = models.BooleanField(default=False, verbose_name="Onay Durumu")
    firstName = models.CharField(max_length=255, verbose_name="Ad")
    lastName = models.CharField(max_length=255, verbose_name="Soyad")
    email = models.EmailField(verbose_name="E-posta")
    phoneNumber = models.CharField(max_length=30, verbose_name="Telefon Numarası")
    rating = models.IntegerField(default=1, verbose_name="Yıldız Puanı", choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField(verbose_name="Yorum")
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Adresi")

    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


class PopupAd(models.Model):
    content = models.TextField(
        verbose_name="Reklam İçeriği",
        help_text="HTML veya metin içerik."
    )
    sites = models.ManyToManyField(
        Site,
        related_name="popup_ads",
        verbose_name="Bağlı Siteler",
        help_text="Bu reklamın gösterileceği siteler."
    )
    isActive = models.BooleanField(
        default=True,
        verbose_name="Aktif",
        help_text="Reklam aktif mi?"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updatedAt = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )

    class Meta:
        verbose_name = "Pop-up Reklam"
        verbose_name_plural = "Pop-up Reklamları"
        ordering = ['-createdAt']

    def __str__(self):
        return f"Reklam ID: {self.id}, Aktif: {self.isActive}"


class Advertisement(AbstractBaseModel):
    AD_POSITION_CHOICES = [
        ('article', 'Makale İçi'),
        ('sidebar', 'Side Bar'),
        ('topbar', 'Top Bar'),
        ('homepage', 'Anasayfa'),
        ('other', 'Diğer')
    ]

    position = models.CharField(
        max_length=50,
        choices=AD_POSITION_CHOICES,
        verbose_name="Reklam Alanı",
        help_text="Reklamın gösterileceği alanı belirtir."
    )
    image = models.ImageField(
        upload_to='advertisements/',
        verbose_name="Reklam Görseli",
        help_text="Bu alana reklam görselini yükleyin."
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Reklam Linki",
        help_text="Reklama tıklanınca gidilecek URL."
    )

    class Meta:
        verbose_name = "Reklam"
        verbose_name_plural = "Reklamlar"

    def __str__(self):
        return f"{self.site.domain} - {self.get_position_display()} Reklamı"


@receiver(post_delete, sender=Advertisement)
def delete_advertisement_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=Advertisement)
def delete_old_advertisement_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Advertisement.objects.get(pk=instance.pk)
    except Advertisement.DoesNotExist:
        return
    if old_instance.image and old_instance.image != instance.image:
        old_instance.image.delete(save=False)


class VisitorAnalytics(AbstractBaseModel):
    VISIT_TYPE_CHOICES = [
        ('homepage', 'Ana Sayfa'),
        ('article', 'Makale')
    ]

    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        verbose_name='Ziyaret Tipi',
        help_text='Ziyaretin ana sayfa mı yoksa makale mi olduğunu belirtir.'
    )
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='visitor_analytics',
        verbose_name='Makale',
        blank=True,
        null=True
    )
    ip_address = models.GenericIPAddressField(verbose_name='IP Adresi')
    user_agent = models.TextField(verbose_name='Kullanıcı Tarayıcısı')
    referer = models.URLField(blank=True, null=True, verbose_name='Yönlendiren URL')
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name='Ziyaret Tarihi')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ülke')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Şehir')
    device_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Cihaz Türü')
    operating_system = models.CharField(max_length=50, blank=True, null=True, verbose_name='İşletim Sistemi')
    browser = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tarayıcı')
    session_duration = models.IntegerField(blank=True, null=True, verbose_name='Oturum Süresi (saniye)')
    is_bounce = models.BooleanField(default=False, verbose_name='Bounce Durumu', help_text='Ziyaret hemen çıkıldı mı?')

    class Meta:
        verbose_name = "Ziyaretçi İstatistiği"
        verbose_name_plural = "Ziyaretçi İstatistikleri"
        indexes = [
            models.Index(fields=["site"]),  # site_id alanına indeks
            models.Index(fields=["article"]),  # article_id alanına indeks
            models.Index(fields=["visit_date"]),  # Zaman bazlı sorgular için
        ]

    def save(self, *args, **kwargs):
        # Oturum süresi 15 saniyeden azsa bounce olarak kabul et
        if self.session_duration is not None and self.session_duration < 15:
            self.is_bounce = True
        else:
            self.is_bounce = False
        super().save(*args, **kwargs)

    def __str__(self):
        visit_target = "Ana Sayfa" if self.visit_type == 'homepage' else self.article.title
        return f"{visit_target} - {self.ip_address} - {self.visit_date}"


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