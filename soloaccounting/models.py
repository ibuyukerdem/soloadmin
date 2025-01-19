#soloaccounting/models.py
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

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify

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


class Currency(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Para Birimi Kodu",
        help_text="ISO kodu veya kısaltma. Örn: 'USD', 'EUR', 'TRY'."
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Para Birimi Adı",
        help_text="Para biriminin tam adı. Örn: 'ABD Doları', 'Avro', 'Türk Lirası'."
    )
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6,
        verbose_name="Dönüşüm Oranı",
        help_text="Varsayılan para birimine (örn. TL) göre 1 birimin kaç TL olduğunu belirtin. Örn: 1 USD = 20.000000 TL"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Varsayılan Para Birimi",
        help_text="Eğer işaretlerseniz, sistemdeki varsayılan para birimi bu olacaktır."
    )

    class Meta:
        verbose_name = "Para Birimi"
        verbose_name_plural = "Para Birimleri"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Eğer bu para birimi varsayılan yapıldıysa, diğer tüm para birimlerinde is_default = False yap
        if self.is_default:
            Currency.objects.update(is_default=False)
            self.is_default = True
        super(Currency, self).save(*args, **kwargs)


class Category(models.Model):
    """
    Ürün Kategorileri için model.
    Kategoriler ürünleri gruplamak ve filtrelemek için kullanılır.
    Örneğin 'Web Geliştirme', 'Finans', 'E-ticaret' gibi kategoriler.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Kategori Adı",
        help_text="Kategori adını belirtiniz. Örneğin: 'Web Geliştirme', 'E-Ticaret', 'Finans', vb."
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="Kategorinin URL'de kullanılacak kısa adı. Otomatik oluşturulur.",
        blank=True
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Kategori Açıklaması",
        help_text="Kategori ile ilgili açıklama."
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Üst Kategori",
        help_text="Bu kategorinin bir üst kategorisi varsa seçiniz. Boş bırakılırsa ana kategori olur."
    )

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    """
    Product modeli, ürünlerin temel özelliklerini barındırır.
    Artık ürünler bir Kategoriye ait olabilir.
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
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name="Kategori",
        help_text="Bu ürünü ait olduğu kategoriye atayınız."
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
    currency = models.ForeignKey(
        Currency,
        null=True,
        blank=True,
        default=1,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Ürün fiyatının belirtildiği para birimi. Boş bırakılırsa varsayılan para birimi kullanılır."
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

    def get_price_in_default_currency(self):
        """
        Ürünün fiyatını varsayılan para biriminde döndürür.
        Eğer currency boş ise varsayılan para birimi zaten bu üründe kullanılır.
        """
        if self.currency is not None:
            # currency.exchange_rate varsayılan birime göre çevrim oranı
            return self.price * self.currency.exchange_rate
        else:
            # Varsayılan para birimi kullanılıyorsa direk fiyatı döndür
            default_currency = Currency.objects.filter(is_default=True).first()
            if default_currency:
                # Ürün zaten varsayılan para biriminde varsayıyoruz
                return self.price * default_currency.exchange_rate
            return self.price

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


# middleware ile ip kontrolü
class Blacklist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, default="Şüpheli davranış")
    is_active = models.BooleanField(default=True)

    # createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return f"{self.ip_address} - {self.reason} - {'Aktif' if self.is_active else 'Pasif'}"
