#soloaccounting/commerce/admin.py
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, InvoiceAddress, Invoice

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Cart (Sepet) yönetimi:
    Bu ekranda kullanıcıların sepetlerini görüntüleyebilir, uygulanan kupon ve kampanyaları inceleyebilirsiniz.
    """
    list_display = ('id', 'user_display', 'currency', 'coupon', 'created_at', 'updated_at')
    list_filter = ('currency', 'applied_campaigns')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('applied_campaigns',)

    fieldsets = (
        (None, {
            'fields': ('user', 'currency', 'coupon', 'applied_campaigns'),
            'description': (
                "Sepet sahibini, para birimini, uygulanan kuponu ve kampanyaları buradan belirleyin. "
                "Anonim kullanıcılar için user boş kalabilir."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at', 'updated_at'),
            'description': "Sepetin oluşturulma ve güncellenme tarihleri otomatik işlenir."
        }),
    )

    def user_display(self, obj):
        return obj.user.username if obj.user else "Anonim"

    user_display.short_description = "Kullanıcı"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    CartItem (Sepet Ürünü) yönetimi:
    Bu ekranda sepetlere eklenmiş ürünlerin detaylarını görüntüleyebilir, birim fiyat, miktar gibi bilgileri inceleyebilirsiniz.
    """
    list_display = ('cart', 'product_display', 'quantity', 'unit_price', 'line_currency', 'created_at', 'updated_at')
    list_filter = ('line_currency',)
    search_fields = ('product__name', 'cart__user__username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity', 'unit_price', 'line_currency'),
            'description': (
                "Bu satırdaki ürün, miktar, birim fiyat ve para birimi bilgilerini içerir. "
                "Ürün fiyatı eklenme anında sabitlenir."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at', 'updated_at'),
            'description': "Bu ürün satırının oluşturulma ve güncellenme tarihleri otomatik işlenir."
        }),
    )

    def product_display(self, obj):
        return obj.product.name

    product_display.short_description = "Ürün"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order (Sipariş) yönetimi:
    Bu ekranda tamamlanmış siparişleri inceleyebilir, durumunu (pending, paid vb.), IP adresini ve POS cevaplarını görebilirsiniz.
    """
    list_display = ('order_number', 'user', 'total_amount', 'currency', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'currency')
    search_fields = ('order_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'order_number')

    fieldsets = (
        (None, {
            'fields': ('user', 'order_number', 'total_amount', 'currency', 'status'),
            'description': (
                "Siparişin sahibi, toplam tutar, para birimi ve güncel durumunu yönetin. "
                "order_number benzersizdir ve müşteri iletişiminde kullanılır."
            )
        }),
        ("POS Bilgileri", {
            'fields': ('ip_address', 'pos_response_code', 'pos_response_message', 'transaction_id'),
            'description': (
                "Ödeme işlemi sırasında sanal pos'tan gelen yanıt bilgileri. "
                "Hata durumunda mesajı inceleyebilir, işlem kimliğini kaydedebilirsiniz."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at', 'updated_at'),
            'description': "Siparişin oluşturulma ve güncellenme tarihleri otomatik işlenir."
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    OrderItem (Sipariş Ürünü) yönetimi:
    Bu ekranda tamamlanmış siparişlerdeki ürün satırlarını görebilir, ürünün sipariş anındaki adını, fiyatını inceleyebilirsiniz.
    """
    list_display = ('order', 'product_name', 'unit_price', 'quantity', 'created_at')
    search_fields = ('product_name', 'order__order_number')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('order', 'product_id', 'product_name', 'unit_price', 'quantity'),
            'description': (
                "Siparişteki ürün satır bilgileri. Ürün fiyatı ve adı sipariş anında sabitlenir, "
                "ürün daha sonra güncellense bile burada değişmez."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at',),
            'description': "Bu satırın oluşturulma tarihi otomatik işlenir."
        }),
    )


@admin.register(InvoiceAddress)
class InvoiceAddressAdmin(admin.ModelAdmin):
    """
    InvoiceAddress (Fatura Adresi) yönetimi:
    Kullanıcıların eklediği fatura adreslerini yönetebilir, varsayılan adresi belirleyebilirsiniz.
    """
    list_display = ('user', 'display_name', 'city', 'country', 'is_default', 'is_efatura', 'created_at', 'updated_at')
    list_filter = ('is_default', 'is_efatura', 'country')
    search_fields = ('user__username', 'company_name', 'full_name', 'city')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'is_default', 'company_name', 'full_name', 'address_line1', 'address_line2',
                       'city', 'district', 'postal_code', 'country', 'taxOffice', 'identificationNumber', 'is_efatura'),
            'description': (
                "Fatura adresi bilgilerini yönetin. Firma adı veya bireysel ad-soyad girebilirsiniz. "
                "Vergi/TCKN/VAT bilgileri de burada yer alır. 'is_default' ile varsayılan adresi belirleyin."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at', 'updated_at'),
            'description': "Adresin oluşturulma ve güncellenme tarihleri otomatik işlenir."
        }),
    )

    def display_name(self, obj):
        return obj.company_name or obj.full_name

    display_name.short_description = "Ad/Firma"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Invoice (Fatura) yönetimi:
    Kesilmiş faturaları görüntüleyebilir, fatura numarası, tarih, ilgili sipariş ve kullanıcıyı inceleyebilirsiniz.
    """
    list_display = (
    'invoice_number', 'user', 'order', 'total_amount', 'currency', 'is_efatura', 'invoice_date', 'created_at')
    list_filter = ('is_efatura', 'currency')
    search_fields = ('invoice_number', 'user__username', 'order__order_number')
    readonly_fields = ('created_at', 'updated_at', 'invoice_number')

    fieldsets = (
        (None, {
            'fields': ('user', 'order', 'invoice_address', 'invoice_number', 'invoice_date', 'total_amount', 'currency',
                       'is_efatura'),
            'description': (
                "Fatura bilgilerini yönetin. Bu fatura belirli bir siparişe dayanır. "
                "Fatura adresi, fatura numarası, tarih, toplam tutar ve e-fatura durumu burada düzenlenebilir."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': ('created_at', 'updated_at'),
            'description': "Faturanın oluşturulma ve güncellenme tarihleri otomatik işlenir."
        }),
    )
