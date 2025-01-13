import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.urls import path
from django.utils.timezone import localtime

from .forms import CustomAdminAuthenticationForm
from .models import ExtendedSite
from .models import SiteUrun, WebServer, SqlServer, MailServer, DnsServer, \
    OperatingSystem, CustomSiteConfiguration, Blacklist, Menu, \
    Campaign, ConditionType, ActionType, Condition, Action, DealerTargetCampaign, \
    DealerTargetThreshold, DealerTargetAssignment, Coupon, UserSegment, DealerSegment, Product, Category, \
    Currency, Cart, CartItem, Order, OrderItem, InvoiceAddress, Invoice


class CustomAdminSite(AdminSite):
    login_form = CustomAdminAuthenticationForm


custom_admin_site = CustomAdminSite()

# Yönetim paneli URL'sini kullanacak şekilde güncelleyin


urlpatterns = [
    path('admin/', custom_admin_site.urls),
]

# Yönetim paneli başlıklarını `settings.py`'den alarak özelleştiriyoruz
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Yönetim Paneli')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Yönetim Paneli')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Hoş Geldiniz!')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """
    Bu yönetim ekranı, sisteminizde kullanılan para birimlerini düzenlemenizi ve listelemenizi sağlar.
    Kullanıcı dostu açıklamalar sayesinde, yöneticiler değişiklik yaparken neyin ne anlama geldiğini kolayca anlayabilir.
    """

    # Admin panelinde gözükecek alanlar
    list_display = (
        'code',
        'name',
        'exchange_rate',
        'is_default'
    )

    # Üzerine tıklanabilir alan
    list_display_links = ('code', 'name',)

    # Kayıtlarda hızlı arama yaparken kullanılacak alanlar
    search_fields = ('code', 'name',)

    # Değişiklik formunda gruplama yaparak kullanıcıya açıklayıcı bir düzen sunuyoruz
    fieldsets = (
        ("Genel Bilgiler", {
            'description': "Burada para biriminin temel kimlik bilgilerini düzenleyebilirsiniz.",
            'fields': ('code', 'name')
        }),
        ("Dönüşüm Bilgileri", {
            'description': "Bu bölümde para birimini varsayılan para birimine çevirirken kullanılacak oranlar yer almaktadır.",
            'fields': ('exchange_rate', 'is_default')
        }),
    )

    # Filtreleme seçenekleri ile kullanıcının yönetim panelinde kayıtları hızlıca filtrelemesini sağlayın
    list_filter = ('is_default',)

    # Kayıt yapıldığında veya güncellendiğinde kullanıcıya basit bir mesaj gösterebilirsiniz (opsiyonel)
    save_on_top = True


@admin.register(UserSegment)
class UserSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Bu segmenti kullanıcılar için etiketleyin. Örneğin 'Yeni Kullanıcı', 'Sadık Müşteri' vb."
        }),
    )


@admin.register(DealerSegment)
class DealerSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
            'description': "Bayi segment adını ve açıklamasını girin. Örneğin 'Gold Bayi' veya 'Alt Bayi'."
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'parent', 'slug'),
            'description': (
                "Kategori adını ve açıklamasını girin. Üst kategori seçerek hiyerarşik yapı oluşturabilirsiniz. "
                "Slug otomatik oluşturulur, gerekirse elle düzenleyebilirsiniz."
            )
        }),
    )
    # Bu sayede kategorileri hiyerarşik olarak yönetebilir, arama ve filtreleme yapabilirsiniz.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'currency', 'serviceDuration', 'isActive', 'createDate', 'updateDate')
    list_filter = ('isActive', 'category', 'currency')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'createDate', 'updateDate')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category'),
            'description': (
                "Ürün temel bilgilerini girin. İsim, açıklama ve kategorisini belirtin. "
                "Kategori seçerek müşterilerin bu ürünü ilgili kategoride bulmasını kolaylaştırın."
            )
        }),
        ("Fiyat & Süre", {
            'fields': ('serviceDuration', 'price', 'currency', 'isActive'),
            'description': (
                "Hizmet süresi (ay) ve fiyat bilgilerini girin. Ürün pasifse sitede görünmez. "
                "Ayrıca fiyatın belirtilmekte olduğu para birimini seçin. Örneğin, bir blog yazılımı için "
                "hizmet süresi 12 ay olabilir, fiyatı 100 EUR veya 2000 TRY şeklinde girebilir, "
                "para birimi alanından da EUR veya TRY seçebilirsiniz."
            )
        }),
        ("URL Bilgileri", {
            'fields': ('slug',),
            'description': "Ürünün URL yapısını otomatik oluşturur. Genellikle değiştirmeye gerek yok."
        }),
        ("Tarih Bilgileri", {
            'fields': ('createDate', 'updateDate'),
            'description': "Oluşturulma ve güncellenme tarihleri otomatik ayarlanır."
        }),
    )


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 1
    verbose_name = "Koşul"
    verbose_name_plural = "Koşullar"
    help_text = (
        "Bu kampanyanın hangi koşullarda geçerli olacağını belirleyin.<br>"
        "<strong>Örnekler:</strong><br>"
        "- Belirli bir ürünü sepete ekleyen kullanıcılara özel (%10 indirim).<br>"
        "- Sepet tutarı 100 TL üzerinde olan alışverişler için geçerli.<br>"
        "- Yeni kullanıcı segmentine ilk alışverişte indirim.<br><br>"
        "Burada koşulları doğru tanımlayarak kampanyanın hedef kitlesini ve ne zaman devreye gireceğini belirleyebilirsiniz. "
        "Uzun aralar verse de buradaki örnekler size koşul tanımlamayı hatırlatacaktır."
    )


class ActionInline(admin.TabularInline):
    model = Action
    extra = 1
    verbose_name = "Aksiyon"
    verbose_name_plural = "Aksiyonlar"
    help_text = (
        "Koşullar sağlandığında ne yapılacağını belirleyin.<br>"
        "<strong>Örnekler:</strong><br>"
        "- Ürüne %10 indirim uygulama.<br>"
        "- Sepete hediye ürün ekleme.<br>"
        "- Kullanıcıya kupon kodu üretme.<br><br>"
        "Aksiyonlar, koşullar sağlandığında kampanyanın müşteriye sunacağı değeri belirler. "
        "Uzun süre kullanmasanız bile bu örnekler sayesinde aksiyon parametrelerini kolayca hatırlayabilirsiniz."
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'currency',)
    search_fields = ('name', 'description')
    filter_horizontal = ('products',)
    inlines = [ConditionInline, ActionInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active', 'currency',),
            'description': (
                "<strong>Kampanya Tanımlarken İzlenmesi Gereken Adımlar:</strong><br><br>"
                "1. Kampanyanın amacını belirleyin (örn. Yeni müşterileri kazanmak, sadık müşterilere indirim vermek, stok fazlası ürünleri eritmek).<br>"
                "2. Kampanya adı ve açıklamasını girerek amacınızı netleştirin.<br>"
                "3. Zaman aralığı belirleyerek kampanyanın başlangıç ve bitiş tarihlerini planlayın.<br>"
                "4. Hangi ürünlere veya ürün kategorilerine odaklanacağınıza karar verin.<br>"
                "5. Koşulları (Conditions) ekleyin: Bu kampanya hangi durumlarda geçerli?<br>"
                "6. Aksiyonları (Actions) ekleyin: Koşullar sağlandığında müşteriye ne tür bir avantaj sunulacak?<br>"
                "# Dikkat Edilmesi Gereken Noktalar:<br>"
                "- Koşulları gereksiz derecede karmaşık yapmayın. Basit ve anlaşılır koşullar, yönetimi kolaylaştırır.<br>"
                "- Aksiyon parametrelerini (örneğin indirim yüzdesi veya hediye ürün ID'si) doğru girin. Yanlış bir ID, beklenmeyen sonuçlar doğurabilir.<br>"
                "- Zaman aralığını gerçekçi planlayın. Çok uzun süreli kampanyalar bazen esnekliğinizi kısıtlayabilir.<br>"
                "- Ürün seçimini dikkatli yapın. Çok geniş ürün yelpazesi kampanyanın etkisini ölçmeyi zorlaştırabilir.<br>"
                "<br>"
                "Bu tavsiyelere uyarak kampanyalarınızı daha verimli, anlaşılır ve hatasız bir şekilde oluşturabilirsiniz.<br><br><br>"
                "<strong>Kampanya Temel Bilgileri:</strong><br>"
                "- <em>Name</em>: Kampanyaya anlamlı bir isim verin. Örneğin 'Yılbaşı İndirimi' veya 'Yeni Kullanıcıya Hoş Geldin'.<br>"
                "- <em>Description</em>: Kampanyanın ne amaçla yapıldığını, hangi hedef kitleye yönelik olduğunu ve "
                "ne tür indirimler/avantajlar sağladığını kısaca açıklayın. Bu metin gelecekte kampanyayı hatırlamanızı kolaylaştırır.<br>"
                "- <em>Is Active</em>: Kampanyayı aktif etmek istediğinizde bu kutucuğu işaretleyin. Aktif değilse, "
                "kampanya tanımlı olsa bile müşteriler üzerinde etkisi olmayacaktır.<br><br>"
                "Uzun bir süre sonra dönseniz bile kampanya adına ve açıklamasına bakarak ne amaçla oluşturulduğunu anlayabilirsiniz."
            )
        }),
        ("Zaman Aralığı", {
            'fields': ('start_date', 'end_date'),
            'description': (
                "<strong>Kampanyanın Geçerli Olduğu Tarih Aralığı:</strong><br>"
                "- <em>start_date</em>: Kampanyanın başlayacağı tarih ve saat. "
                "Örneğin '2024-12-01 00:00:00' şeklinde girerek 1 Aralık günü sıfırıncı dakikadan itibaren aktif edin.<br>"
                "- <em>end_date</em>: Kampanyanın biteceği tarih ve saat. Eğer boş bırakırsanız süresiz devam eder, "
                "ancak genelde bir bitiş tarihi belirlemek kampanyayı yönetmeyi kolaylaştırır.<br><br>"
                "Örneğin, 'Yılbaşı İndirimi' için 24 Aralık'tan 31 Aralık'a kadar geçerli bir aralık belirleyebilirsiniz. "
                "Böylece uzun aradan sonra baktığınızda hangi dönemlerde kampanya yapıldığını anlayabilir, gelecek yıl benzer bir kampanyayı planlarken referans alabilirsiniz."
            )
        }),
        ("Ürünler", {
            'fields': ('products',),
            'description': (
                "<strong>Kampanyanın Uygulanacağı Ürünler:</strong><br>"
                "- Bu alanı boş bırakırsanız kampanya tüm ürünler için geçerli olabilir. "
                "Ancak bu genelde çok geniş kapsamlı olacağından dikkatli kullanın.<br>"
                "- Belirli ürünleri seçerek kampanyayı daha hedefli hale getirebilirsiniz. Örneğin, "
                "sadece 'Laptop' kategorisindeki ürünlere indirim uygulamak veya sadece 'Blog Yazılımı'nı alanlara hediye modül vermek gibi.<br><br>"
                "Uzun bir aradan sonra tekrar baktığınızda, hangi ürünlere odaklandığınızı bu alandan kolayca anlar, "
                "benzer kampanyaları yeniden kurgulayabilirsiniz."
            )
        }),
    )


@admin.register(ConditionType)
class ConditionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description'),
            'description': "Yeni bir koşul tipi tanımlarken kodunun benzersiz olmasına dikkat edin. Örn: 'USER_SEGMENT', 'PRODUCT_PURCHASED'."
        }),
    )


@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description'),
            'description': "Aksiyon tiplerinin kodlarının da benzersiz olması gerekir. Örn: 'DISCOUNT_FIXED', 'ADD_BACKLINK'."
        }),
    )


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'condition_type', 'user_segment', 'dealer_segment')
    search_fields = ('campaign__name', 'condition_type__name')
    list_filter = ('condition_type', 'user_segment', 'dealer_segment')
    fieldsets = (
        (None, {
            'fields': ('campaign', 'condition_type', 'user_segment', 'dealer_segment', 'params'),
            'description': (
                "Bu alanda kampanyaya bağlı koşulları tanımlayabilirsiniz.<br><br>"
                "<strong>Koşulun Bağlı Olduğu Kampanya:</strong><br>"
                "Bu koşul hangi kampanyaya ait? Önce kampanyanızı seçin.<br><br>"
                "<strong>Koşul Tipi (condition_type):</strong><br>"
                "Kampanyanın ne zaman geçerli olacağına dair temel türü belirtir. Örneğin, "
                "'USER_SEGMENT' bir kullanıcı segmentine yönelik koşuldur, "
                "'MIN_CART_TOTAL' sepet toplamı koşuludur, "
                "'PRODUCT_PURCHASED' belirli bir ürün satın alındığında geçerlidir. "
                "Seçtiğiniz koşul tipine göre 'params' alanında veri girişi yapabilirsiniz.<br><br>"
                "<strong>Kullanıcı / Bayi Segmentleri (user_segment, dealer_segment):</strong><br>"
                "Eğer koşul tipiniz segment bazlı ise (örneğin 'USER_SEGMENT' veya 'DEALER_SEGMENT'), "
                "ilgili segment alanını seçin. Koşul bu segmente ait kullanıcılar/bayiler için devreye girecektir.<br><br>"
                "<strong>Params (Ek Parametreler):</strong><br>"
                "Bu alan koşul tipine göre değişen ek kriterler belirlemenize olanak tanır. "
                "JSON formatında girilmesi önerilir. Params alanını kullanırken uzun süreli "
                "unutmalara karşı aşağıdaki örnekleri rehber olarak kullanabilirsiniz:<br><br>"

                "<em>Örnekler:</em><br>"
                "<strong>1) Belirli Ürün Alımı (PRODUCT_PURCHASED)</strong><br>"
                "Koşul: Sepette veya satın alma işleminde belirli bir ürün varsa geçerli olsun.<br>"
                "<code>{\"product_id\": 123}</code><br>"
                "Burada 123 ID'li ürün alındığında koşul sağlanır. Ürünün ID'sini belirleyip params'a ekleyin.<br><br>"

                "<strong>2) Minimum Sepet Tutarı (MIN_CART_TOTAL)</strong><br>"
                "Koşul: Sepet toplamı belirli bir tutarın üzerinde olmalı.<br>"
                "<code>{\"amount\": 100.00}</code><br>"
                "Bu örnekte sepet tutarı 100 TL veya üzerindeyse koşul sağlanır.<br><br>"

                "<strong>3) İlk Alışveriş (FIRST_PURCHASE)</strong><br>"
                "Koşul: Kullanıcının ilk alışverişinde geçerli olsun.<br>"
                "Genellikle ek parametre gerektirmez, ancak isterseniz not koyabilirsiniz:<br>"
                "<code>{\"first_time_only\": true}</code><br>"
                "Böylece yalnızca ilk alışverişte koşul sağlanır.<br><br>"

                "<strong>4) Toplu Alım (BULK_QUANTITY)</strong><br>"
                "Koşul: Belirli bir üründen en az X adet alındığında geçerli olsun.<br>"
                "<code>{\"product_id\": 456, \"min_quantity\": 5}</code><br>"
                "Bu örnekte ürün ID=456 olan üründen en az 5 adet sepete eklenirse koşul sağlanır.<br><br>"

                "<strong>5) Zaman Aralığı (TIME_RANGE)</strong><br>"
                "Koşul: Belirli bir tarih/saat aralığında geçerli olsun.<br>"
                "<code>{\"start_time\": \"2024-12-01T00:00:00Z\", \"end_time\": \"2024-12-31T23:59:59Z\"}</code><br>"
                "Bu örnekte Aralık ayı boyunca koşul geçerli olur.<br><br>"

                "Params alanı esnektir, ihtiyaçlarınıza göre yeni anahtar-değer çiftleri ekleyebilirsiniz. "
                "Ancak formata dikkat edin: JSON formatında olmalı. Örneğin, tırnaklar ve virgüller doğru kullanılmalı. "
                "Uzun süreli aralardan sonra 'params' alanını düzenlerken bu örneklere bakarak hatırlayabilir, "
                "hızlıca yeniden kullanabilirsiniz.<br><br>"

                "Özetle:<br>"
                "- Doğru koşul tipini seçin.<br>"
                "- İlgili segmentleri belirtin (varsa).<br>"
                "- Params'a koşul tipine uygun JSON formatında kriterleri girin.<br><br>"

                "Bu sayede zaman içinde unutulsa dahi, bu açıklamalarla tekrar kolayca hatırlayabilirsiniz."
            )
        }),
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'action_type')
    search_fields = ('campaign__name', 'action_type__name')
    list_filter = ('action_type',)
    fieldsets = (
        (None, {
            'fields': ('campaign', 'action_type', 'params'),
            'description': (
                "Bu alanda kampanyanın koşulları sağlandığında ne yapılacağını belirleyen aksiyonları yönetebilirsiniz.<br><br>"
                "<strong>Aksiyonun Bağlı Olduğu Kampanya:</strong><br>"
                "İlk olarak aksiyonun ait olduğu kampanyayı seçin. Koşullar sağlandığında bu kampanya devreye girecektir.<br><br>"

                "<strong>Aksiyon Tipi (action_type):</strong><br>"
                "Hangi tür aksiyonun uygulanacağını belirler. Örneğin:<br>"
                "- <em>DISCOUNT_PERCENT</em>: Yüzdesel indirim uygular.<br>"
                "- <em>DISCOUNT_FIXED</em>: Sabit tutarlı indirim uygular.<br>"
                "- <em>GIFT_PRODUCT</em>: Sepete hediye ürün ekler.<br>"
                "- <em>ADD_CONTENT</em>: Müşteriye ek içerik (makale, backlink vb.) tanımlar.<br>"
                "- <em>ADD_BACKLINK</em>: Belirli sayıda backlink verilir.<br><br>"

                "<strong>Params (Ek Parametreler):</strong><br>"
                "Aksiyon tipi seçtikten sonra params alanında, JSON formatında aksiyona özel detayları girebilirsiniz. "
                "Uzun süreli aralarda aksiyon parametrelerini unutabilirsiniz, bu yüzden aşağıdaki örnekleri rehber olarak "
                "kullanın.<br><br>"

                "<em>Örnekler:</em><br>"
                "<strong>1) Yüzdesel İndirim (DISCOUNT_PERCENT)</strong><br>"
                "Koşullar sağlandığında ürünün veya sepetin toplam fiyatından belirli bir yüzde indirim yapın.<br>"
                "<code>{\"percentage\": 10}</code><br>"
                "Bu örnekte %10 indirim uygulanır. Yüzde değerini dilediğiniz gibi değiştirebilirsiniz.<br><br>"

                "<strong>2) Sabit İndirim (DISCOUNT_FIXED)</strong><br>"
                "Toplam fiyattan sabit bir tutar düşmek için kullanılır.<br>"
                "<code>{\"value\": 20.00}</code><br>"
                "Bu örnekte 20 TL sabit indirim uygulanır. Değer alanına istediğiniz sabit indirimi yazabilirsiniz.<br><br>"

                "<strong>3) Hediye Ürün (GIFT_PRODUCT)</strong><br>"
                "Belirli bir ürünü ücretsiz olarak sepete eklemek isterseniz kullanın.<br>"
                "<code>{\"product_id\": 789, \"quantity\": 1}</code><br>"
                "Bu örnekte ürün ID=789 olan üründen 1 adet sepete hediye olarak eklenir. İsterseniz miktarı artırabilirsiniz.<br><br>"

                "<strong>4) İçerik Ekleme (ADD_CONTENT)</strong><br>"
                "Müşteriye ek içerik (örn. 100 makale) tanımlamak için kullanılır.<br>"
                "<code>{\"content_type\": \"article\", \"quantity\": 100}</code><br>"
                "Bu örnek 100 adet makale içeriği sunar. content_type alanını 'video', 'pdf' gibi başka türlerde içeriklerle de değiştirebilirsiniz.<br><br>"

                "<strong>5) Backlink Ekleme (ADD_BACKLINK)</strong><br>"
                "Müşteriye belirli sayıda backlink hakkı vermek için kullanılır.<br>"
                "<code>{\"backlinks\": 1000000}</code><br>"
                "Bu örnekte 1.000.000 adet backlink verilir. backlinks değerini dilediğiniz miktara göre güncelleyebilirsiniz.<br><br>"

                "<strong>6) Kupon Üretimi veya Başka Özelleştirilmiş Aksiyonlar (CREATE_COUPON vb.)</strong><br>"
                "Varsayalım yeni bir aksiyon tipi eklediniz: Kupon oluşturmak.<br>"
                "<code>{\"coupon_code\": \"WELCOME50\", \"discount_type\": \"fixed\", \"discount_value\": 50.00}</code><br>"
                "Koşullar sağlandığında 'WELCOME50' kodlu 50 TL değerinde sabit indirim kuponu üretilebilir.<br><br>"

                "Her aksiyon tipi, params alanında kendi ihtiyaçlarına uygun anahtar-değer çiftleri isteyebilir. "
                "Önemli olan, bu alanı JSON formatına uygun doldurmanız (örneklerdeki gibi tırnak ve virgüllere dikkat ederek).<br><br>"

                "Özetle:<br>"
                "- Aksiyon tipini seçin.<br>"
                "- Params alanına, seçtiğiniz aksiyona uygun JSON formatında parametreler girin.<br>"
                "- Uzun süre kullanmasanız bile yukarıdaki örnekler, hatırlamanız için rehber olacaktır.<br><br>"

                "Bu sayede kampanyalarınızın aksiyonlarını esnek bir şekilde yönetebilir, "
                "indirimler, hediye ürünler, içerik eklemeleri ve daha fazlasını kolayca tanımlayabilirsiniz."
            )
        }),
    )


class DealerTargetThresholdInline(admin.TabularInline):
    model = DealerTargetThreshold
    extra = 1
    verbose_name = "Hedef Barem"
    verbose_name_plural = "Hedef Baremleri"
    fieldsets = (
        (None, {
            'fields': ('min_sales_amount', 'credit_reward', 'currency'),
            'description': (
                "<strong>Barem Tanımlama:</strong><br>"
                "Bu alanlar, bayi hedef kampanyasında belirli satış seviyelerine ulaşan bayilere hangi kredinin verileceğini belirler.<br><br>"
                "<strong>min_sales_amount:</strong> Bayinin bu bareme ulaşması için gereken minimum satış tutarı. "
                "Örneğin '50000.00' girerseniz, 50.000 TL üzerinde satış yapan bayi bu bareme ulaşır.<br>"
                "<strong>credit_reward:</strong> Bu bareme ulaşıldığında bayiye verilecek kredi miktarı. "
                "Örneğin '100' girdiğinizde 100 kredi verilir.<br><br>"
                "<em>Örnek Senaryolar:</em><br>"
                "- min_sales_amount=50000, credit_reward=100 => 50.000 TL satış yapan bayiye 100 kredi.<br>"
                "- min_sales_amount=100000, credit_reward=250 => 100.000 TL satış yapan bayiye 250 kredi.<br><br>"
                "Bu şekilde bir kampanya kurgulayarak farklı segmentlerdeki bayilere farklı satış hedefleri ve ödüller sunabilirsiniz. "
                "Uzun aradan sonra dönseniz bile bu örnekler ve açıklamalar hedef baremlerini kolayca hatırlamanıza yardımcı olacaktır."
            )
        }),
    )
    ordering = ['min_sales_amount']


@admin.register(DealerTargetCampaign)
class DealerTargetCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'currency',)
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active', 'currency',),
            'description': (
                "# Ek Notlar:<br>"
                "# Hedef Kampanya Oluştururken İpuçları:<br>"
                "# 1. Kampanya amacınızı belirleyin: Örneğin, bayileri daha yüksek satışa teşvik etmek için 6 aylık bir hedef koyabilirsiniz.<br>"
                "# 2. Tarih aralığını gerçekçi seçin: Çok kısa bir dönem bayilere yeterli satış zamanı vermeyebilir, çok uzun bir dönem ise hedefin anlamını kaybettirebilir.<br>"
                "# 3. Hedef baremleri mantıklı sıralayın: Daha küçük tutarlara daha az kredi, daha büyük tutarlara daha yüksek kredi vererek aşamalı bir ödül sistemi kurun.<br>"
                "# 4. Kampanya bittiğinde raporlama yaparak hangi bayilerin hangi bareme ulaştığını değerlendirip kredileri hesaplarına ekleyin.<br>"
                "#<br>"
                "# Bu bilgilerle donatılmış olarak, kampanyanızı planlamak, uygulamak ve ileride tekrar incelemek çok daha kolay ve hatasız hale gelecektir.<br><br>"
                "<strong>Hedef Kampanya Bilgileri:</strong><br>"
                "- <em>Name</em>: Hedef kampanyasına anlaşılır bir isim verin. Örneğin '2024 İlk Yarı Satış Hedefi' veya 'Alt Bayiler için Yıl Sonu Hedefi'.<br>"
                "- <em>Description</em>: Kampanyanın amacını, hangi bayi segmentlerine yönelik olduğunu veya hangi ürün kategorilerine odaklandığını kısaca özetleyin. "
                "Bu metin ileride kampanyayı anımsarken rehber olacaktır.<br>"
                "- <em>Is Active</em>: Kampanyayı aktif hale getirmek için bu kutucuğu işaretleyin. Aktif değilse, tanımlı olsa bile hedefler ve krediler geçersiz kalır.<br><br>"
                "Uzun süre kullanmasanız bile kampanya adını ve açıklamasını okuyarak ne amaçla oluşturduğunuzu hemen hatırlayabilirsiniz."
            )
        }),
        ("Zaman Aralığı", {
            'fields': ('start_date', 'end_date'),
            'description': (
                "<strong>Kampanyanın Süresi:</strong><br>"
                "- <em>start_date</em>: Kampanyanın başlayacağı tarih. "
                "Örneğin 1 Ocak'tan 30 Haziran'a kadar sürecek bir ilk yarı hedefi için start_date=2024-01-01 şeklinde belirleyebilirsiniz.<br>"
                "- <em>end_date</em>: Kampanyanın biteceği tarih. Eğer 2024-06-30 olarak ayarlarsanız, bu tarihten sonra yapılan satışlar hedefe dahil edilmez.<br><br>"
                "Böylece uzun aradan sonra baktığınızda hangi dönemde bayilerin performansının ölçüldüğünü hemen anlarsınız. "
                "Benzer hedefleri gelecek yıllarda da planlarken bu tarihleri referans alabilirsiniz."
            )
        }),
    )
    inlines = [DealerTargetThresholdInline]


@admin.register(DealerTargetAssignment)
class DealerTargetAssignmentAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'target_campaign')
    search_fields = ('dealer__username', 'target_campaign__name')
    list_filter = ('target_campaign',)
    fieldsets = (
        (None, {
            'fields': ('dealer', 'target_campaign', 'params'),
            'description': (
                "<strong>Bu Ekranın Amacı:</strong><br>"
                "Bir bayi için özel bir hedef kampanyası atamak veya var olan hedef kampanyasını bireysel parametrelerle özelleştirmek "
                "amacıyla kullanılır. Normalde tüm bayiler aynı hedef baremlerinden etkilenebilir, ancak burada belirli bir bayiye "
                "farklı veya ek koşullar tanımlayarak hedefi esnek hale getirebilirsiniz.<br><br>"

                "<strong>Neler Yapılabilir?</strong><br>"
                "- <em>Dealer</em>: Hangi bayiye özel bir atama yapacağınızı seçin. Sadece bayi kullanıcılar listelenir.<br>"
                "- <em>Target Campaign</em>: Bu bayiye hangi hedef kampanyasını atayacağınıza karar verin. Örneğin, '2024 İlk Yarı Satış Hedefi'.<br>"
                "- <em>Params</em>: Burada JSON formatında ek parametreler tanımlayabilirsiniz. Bu parametreler, o bayinin hedef kampanyasında "
                "farklı baremler, ek indirimler veya özel koşullar gibi varyasyonları tanımlamak için kullanılabilir.<br><br>"

                "<strong>Params Alanı Örnekleri:</strong><br>"
                "- <code>{\"custom_min_sales\": 75000}</code>: Bu bayi için minimum satış hedefini 75.000 TL'ye çıkarabilir ve bu tutarın "
                "üzerinde ek kredi verebilirsiniz. Bu sayede genel kampanyadan farklı, sadece bu bayiye özgü bir hedef belirlenmiş olur.<br>"
                "- <code>{\"priority\": \"high\", \"extra_reward\": 50}</code>: Bu bayiye yüksek öncelik tanımlayıp, baremi aştığında ek 50 kredi daha verebilirsiniz.<br>"
                "- <code>{\"excluded_categories\": [\"Finans\", \"E-Ticaret\"]}</code>: Bu bayinin hedef değerlendirmesine Finans ve E-Ticaret kategorilerindeki satışlar dâhil edilmeyebilir, "
                "böylece daha özel bir değerlendirme kurgulayabilirsiniz.<br><br>"

                "<strong>Dikkat Edilmesi Gereken Noktalar:</strong><br>"
                "- Params alanını kullanırken JSON formatına uyun (tırnak işaretleri, virgüller vb.).<br>"
                "- Belirlediğiniz ek parametrelerin arka planda nasıl değerlendirileceğini geliştirici ekiple önceden belirleyin. "
                "Mesela 'custom_min_sales' parametresinin kod tarafında nasıl işleneceği net olmalı.<br>"
                "- Bayiye özel ayarlamalar, kampanyanın adaletini veya tutarlılığını etkileyebilir; bu nedenle bu özelliği dikkatli kullanın.<br><br>"

                "Uzun bir süre bu ekranı kullanmasanız bile, yukarıdaki açıklamalar ve örnekler sayesinde tekrar döndüğünüzde "
                "bayi hedef atamalarını ve params alanını kolaylıkla hatırlayacak, esnek bir bayi hedef yönetimi yapabileceksiniz."
            )
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'discount_value', 'currency', 'is_active', 'start_date', 'end_date', 'usage_limit',
        'used_count'
    )
    list_filter = ('discount_type', 'is_active', 'user_segment', 'dealer_segment', 'currency',)
    search_fields = ('code', 'description')
    filter_horizontal = ('products',)
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'is_active', 'currency',),
            'description': (
                "<strong>Kupon Temel Bilgileri:</strong><br>"
                "- <em>Code</em>: Müşteri tarafından girilecek kupon kodunu belirleyin. Örneğin 'WELCOME10' veya 'BLACKFRIDAY'.<br>"
                "- <em>Description</em>: Bu kuponun ne işe yaradığı, hangi kampanya veya promosyonla ilişkili olduğu gibi notları buraya girebilirsiniz. "
                "Uzun süre sonra dönüp baktığınızda kuponun amacını hatırlamak kolay olacaktır.<br>"
                "- <em>Is Active</em>: Kuponun devrede olup olmadığını belirler. Aktif olmazsa müşteri kuponu kullansa bile geçerli sayılmaz."
            )
        }),
        ("İndirim Bilgileri", {
            'fields': ('discount_type', 'discount_value'),
            'description': (
                "<strong>İndirim Tipi ve Değeri:</strong><br>"
                "- <em>discount_type</em>: Yüzdesel mi sabit mi? 'percent' seçerseniz örneğin %10 indirim, "
                "'fixed' seçerseniz 50 TL sabit indirim gibi senaryolar mümkündür.<br>"
                "- <em>discount_value</em>: İndirim miktarını girin. Örneğin yüzdesel için '10' => %10 indirim, "
                "sabit için '20' => 20 TL indirim. Uzun süre sonra da bu alanı okuyup kolayca uygulayabilirsiniz.<br><br>"
                "Örnekler:<br>"
                "- Yüzdesel indirim: 'percent' ve '10.00' => Sepette %10 indirim.<br>"
                "- Sabit indirim: 'fixed' ve '50.00' => Sepette 50 TL indirim."
            )
        }),
        ("Zaman ve Kullanım Limiti", {
            'fields': ('start_date', 'end_date', 'usage_limit', 'used_count'),
            'description': (
                "<strong>Kuponun Geçerli Olduğu Süre ve Kullanım Sınırları:</strong><br>"
                "- <em>start_date - end_date</em>: Kuponun hangi tarihten hangi tarihe kadar geçerli olacağını belirleyin. "
                "Örneğin yılbaşı indirimi için 'start_date': 2024-12-20, 'end_date': 2024-12-31 gibi. "
                "Uzun aradan sonra baktığınızda da tarih aralığını kontrol etmek kolay olacaktır.<br>"
                "- <em>usage_limit</em>: Kupon kaç kere kullanılabilir? Eğer 100 olarak girerseniz, ilk 100 müşteri kullanır. "
                "Sonrasında kupon devre dışı kalır.<br>"
                "- <em>used_count</em>: Kuponun kaç kez kullanıldığını gösterir. Bu alan otomatik artar. "
                "Manuel düzenlemeyle geçmiş kullanımları resetleyebilir veya inceleyebilirsiniz.<br><br>"
                "Örnekler:<br>"
                "- Sadece Black Friday günü geçerli: start_date = 2024-11-29, end_date = 2024-11-29.<br>"
                "- Sınırlı kullanım: usage_limit = 50 => İlk 50 müşteriye özel."
            )
        }),
        ("Hedef Kitle ve Ürünler", {
            'fields': ('user_segment', 'dealer_segment', 'products'),
            'description': (
                "<strong>Kuponun Kimlere ve Hangi Ürünlere Uygulanacağı:</strong><br>"
                "- <em>user_segment</em>: Örneğin 'Yeni Kullanıcı' segmentini seçerseniz, sadece ilk defa alışveriş yapan kullanıcılar bu kuponu kullanabilir.<br>"
                "- <em>dealer_segment</em>: Bir bayi segmenti seçerseniz, sadece belirli segmentteki bayiler bu kupondan faydalanır. "
                "Örneğin 'Gold Bayi' segmentini seçerseniz, yalnızca 'Gold Bayi' statüsündeki kullanıcılar kuponu kullanabilir.<br>"
                "- <em>products</em>: Bu kuponun sadece belirli ürünlerde mi geçerli olacağını belirleyin. Eğer boş bırakırsanız tüm ürünlerde geçerli olabilir. "
                "Ürünler arasından çoklu seçim yapabilir, uzun süre sonra ürün portföyünüz genişlediğinde belirli ürünlere odaklanabilirsiniz.<br><br>"
                "Örnekler:<br>"
                "- user_segment = 'Sadık Müşteri' => Sadece 3 veya daha fazla alışveriş yapmış müşterilere özel kupon.<br>"
                "- dealer_segment = 'Gold Bayi' => Sadece Gold Bayi segmentindeki bayiler kullanabilir.<br>"
                "- products seçildiğinde: Sadece seçtiğiniz ürünlerde kupon geçerli olur, diğer ürünlerde kullanılamaz."
            )
        }),
    )


class MenuAdminForm(forms.ModelForm):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("superuser", "Superuser"),
    ]

    roles = forms.MultipleChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Roles"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance.roles, list):
            self.fields["roles"].initial = self.instance.roles

    def clean_roles(self):
        return self.cleaned_data.get("roles", [])

    class Meta:
        model = Menu
        fields = "__all__"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm
    list_display = (
        'title',
        'path',
        'icon',
        'caption',
        'parent',
        'product',
        'order',
        'is_superuser_only',
        'disabled',
        'external'
    )  # `id` list_display'den kaldırıldı
    search_fields = ('title', 'path', 'icon', 'caption')  # Arama alanları
    list_filter = ('parent', 'product', 'is_superuser_only', 'disabled', 'external')  # Filtreleme
    ordering = ('order',)  # Sıralama
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'path',
                'icon',
                'caption',
                'parent',
                'product',
                'order'
            )
        }),
        ('Visibility & Access', {
            'fields': (
                'is_superuser_only',
                'roles',
                'disabled',
                'external'
            )
        }),
        ('Metadata', {
            'fields': ('info',)
        }),
    )


@admin.register(SiteUrun)
class SiteUrunAdmin(admin.ModelAdmin):
    list_display = ('site', 'urun_list', 'createdAt')
    search_fields = ('site__name', 'urun__name')
    list_filter = ('site',)
    filter_horizontal = ('urun',)

    def urun_list(self, obj):
        return ", ".join([urun.name for urun in obj.urun.all()])

    urun_list.short_description = "Ürünler"


def safe_remove(file_path):
    """
    Dosyayı güvenli bir şekilde siler. Dosya mevcut değilse hata vermez.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Silindi: {file_path}")


class SiteAdminForm(forms.ModelForm):
    """
    Site admini için form.
    """
    is_active = forms.BooleanField(label="Aktif", required=False)
    is_our_site = forms.BooleanField(label="Bizim Sitemiz", required=False)
    is_default_site = forms.BooleanField(label="Varsayılan Site", required=False)
    show_popup_ad = forms.BooleanField(label="Pop-up Reklam Gösterimi", required=False)
    logo = forms.ImageField(label="Site Logosu", required=False)

    def clean_logo(self):
        """
        Admin panelinden 'logo' alanı temizlendiğinde fiziksel dosyayı da siler ve veritabanı kaydını temizler.
        """
        logo = self.cleaned_data.get("logo", None)

        # ExtendedSite ile bağlantılı olan logo alanını kontrol edin
        if self.instance.pk:
            extended_site = getattr(self.instance, "extended_site", None)
            if extended_site and not logo and extended_site.logo:
                # Logo temizlenmişse fiziksel dosyayı sil
                safe_remove(extended_site.logo.path)
                extended_site.logo = None  # Veritabanındaki logo alanını temizle
                extended_site.save()  # Değişiklikleri kaydet

        return logo

    class Meta:
        model = Site
        fields = "__all__"

    def clean_logo(self):
        """
        Admin panelinden 'logo' alanı temizlendiğinde fiziksel dosyayı da siler ve veritabanı kaydını temizler.
        """
        logo = self.cleaned_data.get("logo", None)

        # ExtendedSite ile bağlantılı olan logo alanını kontrol edin
        if self.instance.pk:
            extended_site = getattr(self.instance, "extended_site", None)
            if extended_site and not logo and extended_site.logo:
                # Logo temizlenmişse fiziksel dosyayı sil
                safe_remove(extended_site.logo.path)
                extended_site.logo = None  # Veritabanındaki logo alanını temizle
                extended_site.save()  # Değişiklikleri kaydet

        return logo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extended_site = getattr(self.instance, "extended_site", None)
        if extended_site:
            self.fields["is_active"].initial = extended_site.isActive
            self.fields["is_our_site"].initial = extended_site.isOurSite
            self.fields["is_default_site"].initial = extended_site.isDefault
            self.fields["show_popup_ad"].initial = extended_site.showPopupAd
            if extended_site.logo:
                self.fields["logo"].initial = extended_site.logo


class SiteAdmin(admin.ModelAdmin):
    """
    Site modeli için admin yapılandırması.
    """
    form = SiteAdminForm
    list_display = (
        "domain", "name", "is_active", "is_our_site", "is_default", "show_popup_ad",
        "formatted_created_at", "formatted_updated_at"  # Tarih alanları listede görünür
    )
    readonly_fields = ("formatted_created_at", "formatted_updated_at")  # Detay görünümünde yalnızca okunabilir alanlar
    search_fields = ("domain", "name")

    def is_active(self, obj):
        return getattr(obj.extended_site, "isActive", False)

    is_active.boolean = True
    is_active.short_description = "Aktif"

    def is_our_site(self, obj):
        return getattr(obj.extended_site, "isOurSite", False)

    is_our_site.boolean = True
    is_our_site.short_description = "Bizim Sitemiz"

    def is_default(self, obj):
        return getattr(obj.extended_site, "isDefault", False)

    is_default.boolean = True
    is_default.short_description = "Varsayılan Site"

    def show_popup_ad(self, obj):
        return getattr(obj.extended_site, "showPopupAd", False)

    show_popup_ad.boolean = True
    show_popup_ad.short_description = "Pop-up Reklam"

    def logo_display(self, obj):
        extended_site = obj.extended_site
        if extended_site and extended_site.logo:
            return f'<img src="{extended_site.logo.url}" style="width:48px; height:auto;" alt="Logo"/>'
        return "Logo Yok"

    logo_display.short_description = "Logo"
    logo_display.allow_tags = True

    def formatted_created_at(self, obj):
        """
        Oluşturulma tarihini okunabilir formatta döndürür.
        """
        extended_site = getattr(obj, "extended_site", None)
        if extended_site and extended_site.createdAt:
            return localtime(extended_site.createdAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_created_at.short_description = "Oluşturulma Tarihi"

    def formatted_updated_at(self, obj):
        """
        Güncellenme tarihini okunabilir formatta döndürür.
        """
        extended_site = getattr(obj, "extended_site", None)
        if extended_site and extended_site.updatedAt:
            return localtime(extended_site.updatedAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_updated_at.short_description = "Güncellenme Tarihi"

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

        if "logo" in form.cleaned_data:
            if not form.cleaned_data["logo"]:
                if extended_site.logo:
                    safe_remove(extended_site.logo.path)
                extended_site.logo = None
            else:
                extended_site.logo = form.cleaned_data["logo"]

        extended_site.save()


# Site modelini yeni admin yapılandırmasıyla kaydetme
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "createdAt", "updatedAt")
    search_fields = ("name", "version")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("name", "version")}),
        ("Açıklama", {"fields": ("description",)}),
        ("Tarih Bilgileri", {"fields": ("createdAt", "updatedAt")}),
    )


@admin.register(WebServer)
class WebServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(SqlServer)
class SqlServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(MailServer)
class MailServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


@admin.register(DnsServer)
class DnsServerAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "isActive",
        "isDefault",
        "ns1",
        "ns2",
        "operatingSystem",
        "paymentType",
        "priceUsd",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("domain", "ns1", "ns2")
    list_filter = ("paymentType", "operatingSystem")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {"fields": ("operatingSystem", "domain", "isActive", "isDefault", "ns1", "ns2")}),
        ("IP Adresleri", {"fields": ("ipAddress1", "ipAddress2", "ipAddress3", "ipAddress4", "ipAddress5")}),
        ("Kullanıcı Bilgileri", {"fields": ("username", "password")}),
        ("Ödeme ve Ücretlendirme", {"fields": ("paymentType", "priceUsd")}),
        ("Diğer Bilgiler", {"fields": ("description", "createdAt", "updatedAt")}),
    )


class BlacklistAdmin(admin.ModelAdmin):
    """
    Karalisteye alınan IP adreslerini yönetir.
    """
    list_display = ("ip_address", "reason", "added_on", "is_active")
    list_filter = ("is_active", "added_on")
    search_fields = ("ip_address", "reason")
    fieldsets = (
        (None, {
            "fields": ("ip_address", "reason", "is_active"),
            "description": "Karalisteye alınacak IP adresi ve nedeni."
        }),
        ("Tarih Bilgileri", {
            "fields": ("added_on",),
            "description": "IP'nin ne zaman karalisteye alındığı bilgisi.",
        }),
    )
    readonly_fields = ("added_on",)


class CustomSiteConfigurationAdmin(admin.ModelAdmin):
    """
    Site konfigürasyonlarını yönetir.
    """
    list_display = (
        "site", "webServer", "sqlServer", "mailServer", "dnsServer", "formatted_created_at", "formatted_updated_at")
    list_filter = ("site", "webServer", "sqlServer", "mailServer", "dnsServer")
    search_fields = ("site__name", "webServer__domain", "sqlServer__domain", "mailServer__domain", "dnsServer__domain")
    readonly_fields = ("createdAt", "updatedAt")
    fieldsets = (
        (None, {
            "fields": ("site",),
            "description": "Bu konfigürasyonun ait olduğu siteyi belirtin."
        }),
        ("Sunucu Konfigürasyonları", {
            "fields": ("webServer", "sqlServer", "mailServer", "dnsServer"),
            "description": "Siteye bağlı sunucu yapılandırmalarını seçin."
        }),
        ("Tarih Bilgileri", {
            "fields": ("createdAt", "updatedAt"),
            "description": "Konfigürasyonun oluşturulma ve güncellenme tarihleri."
        }),
    )

    def formatted_created_at(self, obj):
        if obj.createdAt:
            return localtime(obj.createdAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_created_at.short_description = "Oluşturulma Tarihi"

    def formatted_updated_at(self, obj):
        if obj.updatedAt:
            return localtime(obj.updatedAt).strftime('%d-%m-%Y %H:%M:%S')
        return "Bilinmiyor"

    formatted_updated_at.short_description = "Güncellenme Tarihi"


# Modelleri admin paneline kaydediyoruz
admin.site.register(Blacklist, BlacklistAdmin)
admin.site.register(CustomSiteConfiguration, CustomSiteConfigurationAdmin)


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
