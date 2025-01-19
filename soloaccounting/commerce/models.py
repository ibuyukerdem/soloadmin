#soloaccounting/commerce/models.py
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from soloaccounting.campaigns.models import Campaign
from soloaccounting.campaigns.models import Coupon

# solofor.com eticaret tabloları
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
        'soloaccounting.Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Sepet Para Birimi",
        help_text="Sepetin para birimini belirtin. Ürünler farklı para biriminde olabilir, ancak "
                  "hesaplamaları tek bir para biriminde yapmak için bu alan kullanılır."
    )
    coupon = models.ForeignKey(
        Coupon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Uygulanan Kupon",
        help_text="Bu sepete bir kupon kodu uygulandıysa buradan seçilir.",
        related_name='carts_with_coupon'
    )
    applied_campaigns = models.ManyToManyField(
        Campaign,
        blank=True,
        verbose_name="Uygulanan Kampanyalar",
        help_text="Bu sepete hangi kampanyaların uygulandığını göstermek için kullanılır. "
                  "Kampanya indirimleri hesaplanırken bu alan referans alınabilir.",
        related_name='carts_with_applied_campaigns'
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
            from soloaccounting.models import Currency
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
            from soloaccounting.models import Currency
            current_currency = Currency.objects.filter(is_default=True).first()
        else:
            current_currency = self.currency

        if from_currency is None:
            from soloaccounting.models import Currency
            from_currency = Currency.objects.filter(is_default=True).first()

        # amount * (from_currency.exchange_rate / current_currency.exchange_rate)
        return amount * (from_currency.exchange_rate / current_currency.exchange_rate)


class CartItem(models.Model):
    """
    Sepetteki her bir ürünü temsil eder.
    Burada ürünün o andaki fiyatı, para birimi sabitlenir. Böylece fiyat değişse bile siparişteki ürün fiyatı sabit kalır.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Sepet")
    product = models.ForeignKey('soloaccounting.Product', on_delete=models.CASCADE, verbose_name="Ürün")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miktar")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Birim Fiyat",
        help_text="Ürünün sepete eklendiği andaki birim fiyatı."
    )
    line_currency = models.ForeignKey(
        'soloaccounting.Currency',
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
            from soloaccounting.models import Currency
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
        'soloaccounting.Currency',
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
        'soloaccounting.Currency',
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
