"""
solopayment/admin.py

Bu dosya, e-tahsilat sisteminde kullanılan modellerin Django Admin konfigürasyonlarını içerir.
Filtreleme, arama, listeleme gibi özelliklere ek olarak, kullanıcı dostu yardımlar
('help_text') ve karmaşık alanlar için ek açıklamalar ('description') gösterilmektedir.

Modeller:
- PaymentProvider
- PaymentMethod
- PaymentFee
- PaymentTransaction

Özellikler:
- fieldsets: Alanları mantıksal gruplara ayırarak açıklama ('description') ekler.
- formfield_for_dbfield: Belirli alanlara ek 'help_text' ekleyerek kullanıcı dostu ipuçları sağlar.
- inline: PaymentFee, PaymentMethod içinde satır içi düzenlenebilir (örnek).

Kullanım:
- Bu dosyayı 'solopayment/admin.py' yolunda saklayın.
- Gerekliyse projenizin 'settings.py' içinde 'INSTALLED_APPS' altında 'solopayment' uygulamasını tanımlayın.
"""

from django.contrib import admin
from .models import (
    PaymentProvider,
    PaymentMethod,
    PaymentFee,
    PaymentTransaction
)


# ------------------------------------------------------------------------
# Inline Örnek: PaymentFee, PaymentMethod ekranında gösterilir
# ------------------------------------------------------------------------
class PaymentFeeInline(admin.TabularInline):
    """
    PaymentMethod Admin ekranında PaymentFee kayıtlarını
    satır içi (inline) olarak göstermek için kullanılır.
    """
    model = PaymentFee
    extra = 0  # Yeni ek satır varsayılan sayısı
    fields = (
        'installmentCount',
        'fixedFee',
        'percentageFee',
        'isActive',
    )
    can_delete = True


# ------------------------------------------------------------------------
# PaymentProvider Admin
# ------------------------------------------------------------------------
@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    """
    PaymentProvider: Tüm siteler tarafından paylaşılan ödeme sağlayıcı kayıtlarını yönetir.
    Karmaşık alan açıklamalarına örnek olacak bir 'formfield_for_dbfield' kullanımını da içerir.
    """

    list_display = (
        'id',
        'providerName',
        'providerCode',
        'isActive',
        'createDate',
        'updateDate'
    )
    list_filter = (
        'isActive',
        'createDate',
        'updateDate'
    )
    search_fields = (
        'providerName',
        'providerCode',
        'description'
    )
    ordering = ('providerName',)
    date_hierarchy = 'createDate'
    list_display_links = ('id', 'providerName')

    fieldsets = (
        ("Genel Bilgiler", {
            'fields': (
                'providerName',
                'providerCode',
                'description',
            ),
            'description': "Bu kısımda ödeme sağlayıcının temel bilgilerini girebilirsiniz."
        }),
        ("Durum ve Tarih Bilgileri", {
            'fields': (
                'isActive',
                'createDate',
                'updateDate',
            ),
            'description': "Kaydın aktiflik durumu ve oluşturma/güncelleme tarihleri."
        }),
    )
    readonly_fields = ('createDate', 'updateDate')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Özellikle açıklama gerektiren alanlara ek 'help_text' atamak için override.
        """
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'providerCode':
            formfield.help_text = (
                "Sağlayıcının sistemdeki kısa kodu. Örnek: 'PAYTR', 'SIPAY'."
            )
        elif db_field.name == 'providerName':
            formfield.help_text = (
                "Sağlayıcının görünen adı. Örnek: 'PayTR', 'Sipay', 'Garanti Bankası'."
            )
        elif db_field.name == 'description':
            formfield.help_text = (
                "Sağlayıcı hakkında daha detaylı bilgi veya not girebilirsiniz."
            )
        return formfield


# ------------------------------------------------------------------------
# PaymentMethod Admin
# ------------------------------------------------------------------------
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    PaymentMethod: Belirli bir site için, bir kullanıcı (merchantUser) ile
    ödeme sağlayıcısı arasındaki ayarları yönetir. Örn: API bilgileri, komisyon ödeyicisi vb.
    """
    list_display = (
        'id',
        'site',
        'merchantUser',
        'paymentProvider',
        'defaultForSingleShot',
        'commissionPayer',
        'isActive',
        'createdAt',
        'updatedAt'
    )
    list_filter = (
        'isActive',
        'commissionPayer',
        'defaultForSingleShot',
        'site',
        'createdAt',
        'updatedAt',
    )
    search_fields = (
        'merchantUser__username',  # Kullanıcı (merchant) adı ile arama
        'paymentProvider__providerName',
        'credentials'
    )
    ordering = ('merchantUser',)
    date_hierarchy = 'createdAt'
    list_display_links = ('id', 'merchantUser')

    # PaymentFee kayıtlarını PaymentMethod ekranında inline gösterir
    inlines = [PaymentFeeInline]

    fieldsets = (
        ("İşletme ve Sağlayıcı Bilgileri", {
            'fields': (
                'site',
                'merchantUser',
                'paymentProvider',
            ),
            'description': (
                "Bu bölümde hangi siteye ait olduğu, hangi kullanıcı (işletme) "
                "ve hangi ödeme sağlayıcıyla eşleştiği bilgilerini girebilirsiniz."
            )
        }),
        ("Ödeme Ayarları", {
            'fields': (
                'defaultForSingleShot',
                'commissionPayer',
                'isActive',
            ),
            'description': (
                "Tek çekim için varsayılan yöntem, komisyonu kimin ödeyeceği ve "
                "aktiflik durumu gibi kritik ayarlar burada bulunur."
            )
        }),
        ("Ek Bilgiler", {
            'fields': (
                'credentials',
                'createdAt',
                'updatedAt',
            ),
            'description': (
                "'credentials' alanında sağlayıcıya özgü API anahtarı veya token gibi "
                "ek parametreleri JSON formatında saklayabilirsiniz."
            )
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Özellikle 'credentials' gibi karmaşık alanlara ek 'help_text' atamak için override.
        """
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'credentials':
            formfield.help_text = (
                "Sağlayıcıya özel API bilgileri veya parametreleri JSON formatında saklayın. "
                "Örnek: {\"apiKey\": \"xxx\", \"secretKey\": \"yyy\"}"
            )
        return formfield


# ------------------------------------------------------------------------
# PaymentFee Admin
# ------------------------------------------------------------------------
@admin.register(PaymentFee)
class PaymentFeeAdmin(admin.ModelAdmin):
    """
    PaymentFee: Taksit veya peşin işlemler için komisyon/vade farkı tanımları.
    Örnek: 1 taksit için %2 komisyon, 3 taksit için sabit 5 TL + %1 gibi.
    """
    list_display = (
        'id',
        'site',
        'paymentMethod',
        'installmentCount',
        'fixedFee',
        'percentageFee',
        'isActive',
        'createdAt',
        'updatedAt'
    )
    list_filter = (
        'isActive',
        'site',
        'installmentCount',
        'createdAt',
        'updatedAt'
    )
    search_fields = (
        'paymentMethod__paymentProvider__providerName',
    )
    ordering = ('paymentMethod', 'installmentCount')
    date_hierarchy = 'createdAt'
    list_display_links = ('id', 'paymentMethod')

    fieldsets = (
        ("İlgili Ödeme Yöntemi", {
            'fields': (
                'site',
                'paymentMethod',
            ),
            'description': (
                "Bu ücret tanımının hangi site ve hangi ödeme yöntemi (PaymentMethod) "
                "ile ilişkili olduğunu seçin."
            )
        }),
        ("Ücret Tanımı", {
            'fields': (
                'installmentCount',
                'fixedFee',
                'percentageFee',
                'isActive',
            ),
            'description': (
                "'installmentCount': Kaç taksite uygulanacak.\n"
                "'fixedFee': TL bazında sabit ücret.\n"
                "'percentageFee': Oransal komisyon (%)."
            )
        }),
        ("Tarih Bilgileri", {
            'fields': (
                'createdAt',
                'updatedAt',
            ),
            'description': "Oluşturulma ve güncellenme zaman bilgileri."
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Ek açıklama gerektiren alanlara 'help_text' atamak için override.
        """
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'installmentCount':
            formfield.help_text = (
                "Taksit sayısı. 1 ise peşin işlem anlamına gelebilir."
            )
        elif db_field.name == 'fixedFee':
            formfield.help_text = (
                "Sabit ücret (TL) - işleme eklenir."
            )
        elif db_field.name == 'percentageFee':
            formfield.help_text = (
                "Oransal komisyon. Örnek: 2.50 => %2.50"
            )
        return formfield


# ------------------------------------------------------------------------
# PaymentTransaction Admin
# ------------------------------------------------------------------------
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    PaymentTransaction: Gerçekleşen ödeme işlemlerinin kayıtları.
    Hem giriş yapmış (payingUser) hem de misafir (guest) ödemelerini yönetir.
    """
    list_display = (
        'id',
        'site',
        'merchantUser',
        'payingUser',
        'payerName',
        'paymentMethod',
        'amount',
        'installmentCount',
        'totalPaidAmount',
        'status',
        'referenceCode',
        'createdAt',
        'updatedAt'
    )
    list_filter = (
        'status',
        'site',
        'merchantUser',
        'paymentMethod',
        'createdAt',
        'updatedAt'
    )
    search_fields = (
        'payerName',  # Guest ödeyen adı
        'referenceCode',  # Banka referansı
        'merchantUser__username',
        'paymentMethod__paymentProvider__providerName',
    )
    ordering = ('-createdAt',)  # En yeni işlemler en üstte görünür
    date_hierarchy = 'createdAt'
    list_display_links = ('id', 'merchantUser')

    fieldsets = (
        ("İşlem Kimliği ve Tarih Bilgisi", {
            'fields': (
                'site',
                'createdAt',
                'updatedAt',
            ),
            'description': "Bu bölümde kaydın site bilgisi ve zaman damgaları yer alır."
        }),
        ("İşletme (Merchant) Bilgileri", {
            'fields': (
                'merchantUser',
            ),
            'description': "Ödemeyi alan işletmeyi (kullanıcı) ifade eder."
        }),
        ("Ödeyen Bilgileri", {
            'fields': (
                'payingUser',
                'payerName',
                'payerNote',
            ),
            'description': (
                "Eğer kullanıcı giriş yapmadıysa 'payingUser' boş kalır ve 'payerName' alanı "
                "misafirin adını içerebilir. 'payerNote' misafir notu girmek için kullanılabilir."
            )
        }),
        ("Ödeme Detayları", {
            'fields': (
                'paymentMethod',
                'amount',
                'installmentCount',
                'totalPaidAmount',
                'status',
                'referenceCode',
            ),
            'description': (
                "İşlemin gerçekleştirildiği yöntem, asıl tutar, taksit, "
                "gerçekte ödenen toplam tutar, işlem durumu ve referans bilgisi."
            )
        }),
        ("Komisyon Hesaplamaları", {
            'fields': (
                'calculatedFixedFee',
                'calculatedPercentageFee',
            ),
            'description': (
                "İşlem sırasında hesaplanan sabit veya oransal ücretleri "
                "görüntülemek için kullanılır."
            )
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Özellikle karmaşık alanlara ek 'help_text' mesajları eklemek için override.
        """
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'payerName':
            formfield.help_text = (
                "Ödeyen kişinin adı. Eğer kullanıcı giriş yapmadıysa bu kısım doldurulabilir."
            )
        elif db_field.name == 'payerNote':
            formfield.help_text = (
                "Misafir ödemesi yapan kişi kendi notunu girmek isterse kullanılır."
            )
        elif db_field.name == 'status':
            formfield.help_text = (
                "İşlemin onay, bekleme, hata ya da reddedilme durumunu gösterir."
            )
        elif db_field.name == 'referenceCode':
            formfield.help_text = (
                "Banka veya ödeme sağlayıcısından dönen işlem referansı. Takip için kullanılır."
            )
        return formfield
