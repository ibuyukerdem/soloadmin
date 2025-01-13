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
from django.utils import timezone
from django.utils.text import slugify

import common.models
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


class DealerSegment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Bayi Segmenti Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Bayi Segmenti Açıklaması")

    class Meta:
        verbose_name = "Bayi Segmenti"
        verbose_name_plural = "Bayi Segmentleri"

    def __str__(self):
        return self.name


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


class Campaign(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kampanya Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Kampanya Açıklaması")
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi", null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name='campaigns', verbose_name="Ürünler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Kampanya içindeki indirimlerin, hedeflerin veya tutarların hangi para biriminde tanımlandığını belirtin."
    )

    class Meta:
        verbose_name = "Kampanya"
        verbose_name_plural = "Kampanyalar"

    def __str__(self):
        return self.name


class ConditionType(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Koşul Kodu")
    name = models.CharField(max_length=100, verbose_name="Koşul Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Koşul Açıklaması")

    class Meta:
        verbose_name = "Koşul Tipi"
        verbose_name_plural = "Koşul Tipleri"

    def __str__(self):
        return f"{self.code} - {self.name}"


class ActionType(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Aksiyon Kodu")
    name = models.CharField(max_length=100, verbose_name="Aksiyon Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Aksiyon Açıklaması")

    class Meta:
        verbose_name = "Aksiyon Tipi"
        verbose_name_plural = "Aksiyon Tipleri"

    def __str__(self):
        return f"{self.code} - {self.name}"


class UserSegment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Segment Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Segment Açıklaması")

    class Meta:
        verbose_name = "Kullanıcı Segmenti"
        verbose_name_plural = "Kullanıcı Segmentleri"

    def __str__(self):
        return self.name


class Condition(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='conditions', verbose_name="Kampanya")
    condition_type = models.ForeignKey(ConditionType, on_delete=models.PROTECT, related_name='conditions',
                                       verbose_name="Koşul Tipi")
    params = models.JSONField(default=dict, blank=True, verbose_name="Koşul Parametreleri")
    user_segment = models.ForeignKey(UserSegment, null=True, blank=True, on_delete=models.SET_NULL,
                                     verbose_name="Kullanıcı Segmenti")
    dealer_segment = models.ForeignKey(DealerSegment, null=True, blank=True, on_delete=models.SET_NULL,
                                       verbose_name="Bayi Segmenti")

    class Meta:
        verbose_name = "Koşul"
        verbose_name_plural = "Koşullar"

    def __str__(self):
        return f"{self.campaign.name} - {self.condition_type.name}"


class Action(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='actions', verbose_name="Kampanya")
    action_type = models.ForeignKey(ActionType, on_delete=models.PROTECT, related_name='actions',
                                    verbose_name="Aksiyon Tipi")
    params = models.JSONField(default=dict, blank=True, verbose_name="Aksiyon Parametreleri")

    class Meta:
        verbose_name = "Aksiyon"
        verbose_name_plural = "Aksiyonlar"

    def __str__(self):
        return f"{self.campaign.name} - {self.action_type.name}"


### Bayi Hedef Kampanyaları (DealerTarget)
class DealerTargetCampaign(models.Model):
    """
    Bayilere yönelik hedef kampanyalarının tanımlanması.
    Örneğin: "2024 İlk Yarı Bayi Satış Hedefi"
    """
    name = models.CharField(max_length=255, verbose_name="Hedef Kampanya Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Bu hedef kampanyasındaki satış tutarları ve krediler için hangi para biriminin geçerli olduğunu belirtin."
    )

    class Meta:
        verbose_name = "Bayi Hedef Kampanyası"
        verbose_name_plural = "Bayi Hedef Kampanyaları"

    def __str__(self):
        return self.name


class DealerTargetThreshold(models.Model):
    """
    Bir hedef kampanyası içinde birden fazla barem olabilir.
    Örneğin:
    - 50.000 TL satış => 100 kredi
    - 100.000 TL satış => 250 kredi
    """
    target_campaign = models.ForeignKey(DealerTargetCampaign, on_delete=models.CASCADE, related_name='thresholds',
                                        verbose_name="Hedef Kampanyası")
    min_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Minimum Satış Tutarı")
    credit_reward = models.PositiveIntegerField(verbose_name="Kredi Ödülü")
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Bu barem için belirlenen tutarın para birimini belirtin. Boş bırakılırsa hedef kampanyanın para birimi kullanılır."
    )

    class Meta:
        verbose_name = "Bayi Hedef Barem"
        verbose_name_plural = "Bayi Hedef Baremleri"
        ordering = ['min_sales_amount']

    def __str__(self):
        return f"{self.target_campaign.name} - {self.min_sales_amount} için {self.credit_reward} kredi"


class DealerTargetAssignment(models.Model):
    """
    Her bayiye, belirli bir hedef kampanyası için özel baremler atayabilirsiniz.
    Bu sayede aynı hedef kampanyası farklı bayilere farklı baremlerle uygulanabilir.
    Kullanım opsiyoneldir: Eğer tüm bayiler aynı baremleri paylaşacaksa bu tabloyu kullanmaya gerek olmayabilir.
    """
    dealer = models.ForeignKey(common.models.CustomUser, on_delete=models.CASCADE, limit_choices_to={'isDealer': True},
                               verbose_name="Bayi")
    target_campaign = models.ForeignKey(DealerTargetCampaign, on_delete=models.CASCADE, verbose_name="Hedef Kampanyası")
    # Eğer her bayiye özel ek baremler vermek isterseniz separate tablo tutabilir veya params ile yönetebilirsiniz.
    params = models.JSONField(default=dict, blank=True, verbose_name="Ek Parametreler")

    class Meta:
        verbose_name = "Bayi Hedef Atama"
        verbose_name_plural = "Bayi Hedef Atamaları"

    def __str__(self):
        return f"{self.dealer.username} - {self.target_campaign.name}"


### Kupon Kodları (Coupons)
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Kupon Kodu")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    discount_type = models.CharField(max_length=20, choices=[('percent', 'Yüzde'), ('fixed', 'Sabit')],
                                     verbose_name="İndirim Tipi")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="İndirim Değeri")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kullanım Limiti")
    used_count = models.PositiveIntegerField(default=0, verbose_name="Kullanım Sayısı")
    user_segment = models.ForeignKey(UserSegment, null=True, blank=True, on_delete=models.SET_NULL,
                                     verbose_name="Kullanıcı Segmenti")
    dealer_segment = models.ForeignKey(DealerSegment, null=True, blank=True, on_delete=models.SET_NULL,
                                       verbose_name="Bayi Segmenti")
    products = models.ManyToManyField(Product, blank=True, verbose_name="Geçerli Ürünler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Bu kuponun indirim değerinin hangi para biriminde olduğunu belirtin. Örneğin 'EUR', 'USD', 'TRY'."
    )

    class Meta:
        verbose_name = "Kupon"
        verbose_name_plural = "Kuponlar"

    def __str__(self):
        return self.code

    def is_valid(self, user=None):
        """
        Kuponun geçerli olup olmadığını kontrol edebileceğiniz basit bir metot.
        Tarih, kullanım limiti, kullanıcı segmenti vb. kontrolü burada yapılabilir.
        """
        now = timezone.now()
        if self.is_active is False:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False

        # Kullanıcı segment kontrolü
        if user and not user.isDealer and self.user_segment:
            # Burada kullanıcı ilgili segmentte mi kontrol edebiliriz.
            # Segment logicini siz belirleyebilirsiniz.
            pass

        # Bayi segment kontrolü
        if user and user.isDealer and self.dealer_segment:
            # Kullanıcı bayiyse ve kupon bayilere özel bir segmente aitse
            if user.dealer_segment != self.dealer_segment:
                return False

        return True


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


class Cart(models.Model):
    """
    Kullanıcının sepetini temsil eder.
    Sepetteki ürünlerin toplam fiyatı, kupon/kampanya indirimleri ve seçilen para birimi bilgilerini içerir.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Kullanıcı",
        help_text="Sepet sahibi kullanıcı. Anonim sepet için boş bırakılabilir."
    )
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Sepet Para Birimi",
        help_text="Sepetin para birimini belirtin. Ürünler farklı para biriminde olabilir, ancak "
                  "hesaplamaları tek bir para biriminde yapmak için bu alan kullanılır."
    )
    coupon = models.ForeignKey(
        'Coupon',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Uygulanan Kupon",
        help_text="Bu sepete bir kupon kodu uygulandıysa buradan seçilir."
    )
    applied_campaigns = models.ManyToManyField(
        'Campaign',
        blank=True,
        verbose_name="Uygulanan Kampanyalar",
        help_text="Bu sepete hangi kampanyaların uygulandığını göstermek için kullanılır. "
                  "Kampanya indirimleri hesaplanırken bu alan referans alınabilir."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Sepet"
        verbose_name_plural = "Sepetler"

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonim'} Sepeti - {self.id}"

    def get_subtotal(self):
        """
        Sepetteki ürünlerin toplam fiyatını (indirimler hariç) hesaplar.
        Bu noktada ürünler farklı para biriminde olabilir, tümünü sepetin para birimine çevirmek gerekir.
        """
        subtotal = 0
        if not self.currency:
            # Varsayılan para birimi al
            from .models import Currency
            default_currency = Currency.objects.filter(is_default=True).first()
            current_currency = default_currency
        else:
            current_currency = self.currency

        for item in self.items.all():
            # Ürün satırının para birimini sepet para birimine çevir
            line_price_in_cart_currency = item.get_line_price_in_currency(current_currency)
            subtotal += line_price_in_cart_currency
        return subtotal

    def get_discount_total(self):
        """
        Kupon, kampanya gibi indirimleri hesaplar.
        Bu metot geliştirilebilir ve projenizin gerçek iş mantığına uyarlanmalıdır.
        """
        discount_total = 0

        # Kupon indirimi:
        if self.coupon and self.coupon.is_valid(user=self.user):
            discount_value = self.coupon.discount_value
            # Kuponun para birimi seçili olabilir:
            coupon_currency = self.coupon.currency or self.currency
            # Kupon indirimini sepet para birimine çevir
            discount_in_cart_currency = self._convert_amount_to_cart_currency(discount_value, coupon_currency)

            if self.coupon.discount_type == 'fixed':
                # Sabit tutarlı indirim
                discount_total += discount_in_cart_currency
            elif self.coupon.discount_type == 'percent':
                # Yüzdesel indirim
                subtotal = self.get_subtotal()
                discount_total += (subtotal * (discount_in_cart_currency / 100))

        # Kampanya indirimleri:
        # Bu yapıda, her kampanya aksiyonunun params alanında hangi indirim/hediye parametreleri olabileceğini varsayıyoruz.
        # Örneğin params şu şekilde tanımlanabilir:
        # {
        #   "discount_amount": 50,
        #   "percentage": 10,
        #   "gift_product_id": 123,
        #   "gift_quantity": 1,
        #   "fixed_amount": 20,
        #   "custom_min_sales": 100000  (örneğin belirli bir satış aşılırsa ekstra indirim)
        # }

        subtotal = self.get_subtotal()  # Kampanya yüzdesel indirimlerinde kullanabiliriz.
        for camp in self.applied_campaigns.all():
            camp_currency = camp.currency or self.currency
            for action in camp.actions.all():
                # Sabit tutarlı indirim (discount_amount)
                if 'discount_amount' in action.params:
                    discount_amount = action.params['discount_amount']
                    discount_in_cart_currency = self._convert_amount_to_cart_currency(discount_amount, camp_currency)
                    discount_total += discount_in_cart_currency

                # Yüzdesel indirim (percentage)
                if 'percentage' in action.params:
                    percentage_value = action.params['percentage']
                    # Subtotal üzerinden yüzdesel indirim
                    discount_in_cart_currency = (subtotal * (percentage_value / 100))
                    discount_total += discount_in_cart_currency

                # Sabit tutarlı indirim (fixed_amount)
                # Bu 'discount_amount' ile aynı türde olabilir, ancak projede farklı aksiyonlar için farklı parametreler kullanılıyor olabilir.
                if 'fixed_amount' in action.params:
                    fixed_amount = action.params['fixed_amount']
                    discount_in_cart_currency = self._convert_amount_to_cart_currency(fixed_amount, camp_currency)
                    discount_total += discount_in_cart_currency

                # Hediye ürün ekleme (gift_product_id ve gift_quantity)
                # Bu bir indirim olarak değil, sepetinize ek bir ürün ekleyerek kullanabilirsiniz.
                # Bu örnekte indirim toplamına etki etmiyor, ancak koda gösterim amaçlı ekliyoruz.
                # Hediye ürünü sepete eklemek için separate bir fonksiyon çağrısı yapabilirsiniz.
                if 'gift_product_id' in action.params:
                    gift_product_id = action.params['gift_product_id']
                    gift_quantity = action.params.get('gift_quantity', 1)
                    # Burada hediye ürün ekleme lojikini implement edebilirsiniz:
                    # self.add_gift_product(gift_product_id, gift_quantity)
                    # Bu işlem indirim toplamını doğrudan etkilemeyebilir, ancak müşteriye ek değer katacaktır.

                # Özel koşullar örneği (custom_min_sales)
                # Belirli bir satış tutarı aşılırsa ekstra indirim yapabilirsiniz.
                if 'custom_min_sales' in action.params:
                    required_sales = action.params['custom_min_sales']
                    # required_sales'ı sepete uygulamak için, eğer subtotal bu değeri aşıyorsa ekstra indirim uygulayın
                    custom_threshold_currency = camp_currency  # Varsayım
                    required_sales_in_cart_currency = self._convert_amount_to_cart_currency(required_sales,
                                                                                            custom_threshold_currency)
                    if subtotal >= required_sales_in_cart_currency:
                        # Örneğin bu koşula ulaştığında ekstra 10 birim indirim uygulayın:
                        extra_discount = 10
                        discount_total += self._convert_amount_to_cart_currency(extra_discount,
                                                                                custom_threshold_currency)

        return discount_total

    def get_total(self):
        """
        Sepetin toplam tutarını (indirimler uygulandıktan sonra) hesaplar.
        """
        subtotal = self.get_subtotal()
        discount_total = self.get_discount_total()
        total = subtotal - discount_total
        return total if total > 0 else 0

    def _convert_amount_to_cart_currency(self, amount, from_currency):
        """
        Belirli bir tutarı, sepetin para birimine dönüştürür.
        """
        if not self.currency:
            # Varsayılan para birimi al
            from .models import Currency
            current_currency = Currency.objects.filter(is_default=True).first()
        else:
            current_currency = self.currency

        if from_currency is None:
            from .models import Currency
            from_currency = Currency.objects.filter(is_default=True).first()

        # amount * (from_currency.exchange_rate / current_currency.exchange_rate)
        return amount * (from_currency.exchange_rate / current_currency.exchange_rate)


class CartItem(models.Model):
    """
    Sepetteki her bir ürünü temsil eder.
    Burada ürünün o andaki fiyatı, para birimi sabitlenir. Böylece fiyat değişse bile siparişteki ürün fiyatı sabit kalır.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Sepet")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Ürün")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miktar")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Birim Fiyat",
        help_text="Ürünün sepete eklendiği andaki birim fiyatı."
    )
    line_currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Ürün Satır Para Birimi",
        help_text="Bu satırın para birimi. Ürün eklendiğinde product.currency alınarak set edilebilir."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Sepet Ürünü"
        verbose_name_plural = "Sepet Ürünleri"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_line_total(self):
        """
        Bu satırdaki toplam tutar (line_currency üzerinden).
        """
        return self.unit_price * self.quantity

    def get_line_price_in_currency(self, target_currency):
        """
        Bu satırdaki fiyatı hedef para birimine dönüştürür.
        """
        if not self.line_currency:
            # Ürün eklenirken line_currency set edilmemişse varsayılan para birimi olduğunu varsay
            from .models import Currency
            line_cur = Currency.objects.filter(is_default=True).first()
        else:
            line_cur = self.line_currency

        return self.get_line_total() * (line_cur.exchange_rate / target_currency.exchange_rate)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı",
        help_text="Siparişi veren kullanıcı"
    )
    order_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Sipariş Numarası",
        help_text="Siparişe özel benzersiz numara. Müşteriye gösterilir ve destek taleplerinde kullanılır."
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Toplam Tutar",
        help_text="Siparişin toplam tutarı (indirimler uygulandıktan sonra)."
    )
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi",
        help_text="Siparişin nihai fiyatlandırmasının yapıldığı para birimi."
    )
    status = models.CharField(
        max_length=50,
        default='pending',
        verbose_name="Durum",
        help_text="Siparişin güncel durumu: pending, paid, shipped, failed, refunded vb."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    # Sanal POS bilgileri:
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="Müşteri IP Adresi",
        help_text="Ödeme anında kullanıcının IP adresi"
    )
    pos_response_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="POS Cevap Kodu",
        help_text="Sanal pos tarafından dönen cevap kodu."
    )
    pos_response_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="POS Mesajı",
        help_text="Sanal pos hata veya başarı mesajı."
    )
    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="İşlem ID",
        help_text="Sanal pos tarafından atanan işlem ID'si"
    )

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        # order_number otomatik olarak oluşturulabilir eğer boşsa:
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super(Order, self).save(*args, **kwargs)

    def _generate_order_number(self):
        # Basit bir order number oluşturma yöntemi:
        # İstediğiniz formatta üretebilirsiniz, örn: "ORD-2024-0001"
        return f"SLF-{uuid.uuid4().hex[:8].upper()}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Sipariş"
    )
    product_id = models.PositiveIntegerField(
        verbose_name="Ürün ID",
        help_text="Sipariş verildiği andaki ürün ID. Ürün değişse bile bu ID sabit kalır."
    )
    product_name = models.CharField(
        max_length=255,
        verbose_name="Ürün Adı",
        help_text="Sipariş verildiği andaki ürün adı."
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Birim Fiyat",
        help_text="Sipariş anındaki birim fiyat. Ürün fiyatı daha sonra değişse bile bu sabit kalır."
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Miktar",
        help_text="Siparişteki ürün adedi."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Sipariş Ürünü"
        verbose_name_plural = "Sipariş Ürünleri"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def get_line_total(self):
        return self.unit_price * self.quantity


class InvoiceAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoice_addresses',
        verbose_name="Kullanıcı",
        help_text="Bu fatura adresi hangi kullanıcıya ait?"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Varsayılan Adres",
        help_text="Bu adresi varsayılan fatura adresi olarak işaretleyin."
    )
    # Firma veya bireysel alanlar
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Firma Adı",
        help_text="Kurumsal fatura için firma adı. Bireysel kullanımdaysa boş bırakın."
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Ad Soyad",
        help_text="Bireysel fatura için alıcının tam adı."
    )

    address_line1 = models.CharField(
        max_length=255,
        verbose_name="Adres Satırı 1",
        help_text="Sokak, mahalle vb."
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Adres Satırı 2",
        help_text="Apartman, daire no vb. Ek adres bilgileri."
    )
    city = models.CharField(max_length=100, verbose_name="Şehir")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="İlçe")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Posta Kodu")
    country = models.CharField(max_length=100, verbose_name="Ülke", help_text="Örn: Türkiye, Germany, France vb.")

    # Vergi / Kimlik bilgileri
    taxOffice = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Vergi Dairesi',
        help_text="Türkiye için vergi dairesi, Avrupa ülkeleri için ilgili vergi ofisi"
    )
    identificationNumber = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Kimlik/Şirket Numarası',
        help_text="Bireysel için TC Kimlik no veya yabancı kimlik no, kurumsal için VKN veya Avrupa için VAT Number"
    )

    is_efatura = models.BooleanField(
        default=False,
        verbose_name="E-Fatura Mükellefi",
        help_text="Bu adres e-fatura kesimine uygun mu?"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Fatura Adresi"
        verbose_name_plural = "Fatura Adresleri"

    def __str__(self):
        return f"{self.company_name or self.full_name} - {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        # Eğer bu adres varsayılan olarak işaretlendiyse diğer adreslerden varsayılanı kaldır
        if self.is_default:
            InvoiceAddress.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super(InvoiceAddress, self).save(*args, **kwargs)


class Invoice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı",
        help_text="Bu faturanın kesildiği kullanıcı."
    )
    order = models.ForeignKey(
        'Order',  # varsayıyoruz ki Order modeli daha önce tanımlanmış
        on_delete=models.CASCADE,
        verbose_name="Sipariş",
        help_text="Bu fatura hangi siparişi temsil ediyor?"
    )
    invoice_address = models.ForeignKey(
        InvoiceAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Fatura Adresi",
        help_text="Faturanın kesildiği adres."
    )
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Fatura Numarası",
        help_text="Benzersiz fatura numarası."
    )
    invoice_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fatura Tarihi",
        help_text="Faturanın düzenlenme tarihi."
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Fatura Toplam Tutarı"
    )
    currency = models.ForeignKey(
        'Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Para Birimi"
    )
    is_efatura = models.BooleanField(
        default=False,
        verbose_name="E-Fatura",
        help_text="Eğer bu bir e-fatura ise işaretleyin."
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        super(Invoice, self).save(*args, **kwargs)

    def _generate_invoice_number(self):
        # Basit örnek: "INV-2024-0001" formatında bir numara üretebilir
        # Burada sadece UUID kullanıyoruz. Gerçek hayatta tarih+seri no kombinasyonu yapılabilir.
        return f"INV-{uuid.uuid4().hex[:8].upper()}"
