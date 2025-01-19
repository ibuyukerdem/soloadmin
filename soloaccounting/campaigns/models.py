#soloaccounting/campaigns/models.py

from django.db import models
from django.utils import timezone

class Campaign(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kampanya Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Kampanya Açıklaması")
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi", null=True, blank=True)
    products = models.ManyToManyField('soloaccounting.Product', blank=True, related_name='campaigns', verbose_name="Ürünler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    currency = models.ForeignKey(
        'soloaccounting.Currency',
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


class DealerSegment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Bayi Segmenti Adı")
    description = models.TextField(null=True, blank=True, verbose_name="Bayi Segmenti Açıklaması")

    class Meta:
        verbose_name = "Bayi Segmenti"
        verbose_name_plural = "Bayi Segmentleri"

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
        'soloaccounting.Currency',
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
        'soloaccounting.Currency',
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
    dealer = models.ForeignKey('common.CustomUser', on_delete=models.CASCADE, limit_choices_to={'isDealer': True},
                               verbose_name="Bayi")
    target_campaign = models.ForeignKey(DealerTargetCampaign, on_delete=models.CASCADE, verbose_name="Hedef Kampanyası")
    # Eğer her bayiye özel ek baremler vermek isterseniz separate tablo tutabilir veya params ile yönetebilirsiniz.
    params = models.JSONField(default=dict, blank=True, verbose_name="Ek Parametreler")

    class Meta:
        verbose_name = "Bayi Hedef Atama"
        verbose_name_plural = "Bayi Hedef Atamaları"

    def __str__(self):
        return f"{self.dealer.username} - {self.target_campaign.name}"

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
    products = models.ManyToManyField('soloaccounting.Product', blank=True, verbose_name="Geçerli Ürünler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    currency = models.ForeignKey(
        'soloaccounting.Currency',
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
