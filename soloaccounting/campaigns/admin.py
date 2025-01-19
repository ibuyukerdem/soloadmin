# soloaccounting/campaigns/admin.py
from django.contrib import admin
from .models import Campaign, ConditionType, ActionType, Condition, Action, DealerTargetCampaign, \
    DealerTargetThreshold, DealerTargetAssignment, Coupon, UserSegment, DealerSegment

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
