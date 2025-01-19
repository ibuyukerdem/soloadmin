from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Article, Image, Comment, PopupAd, VisitorAnalytics, SiteSettings, HomePageSettings, \
    FooterSettings, Menu


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1  # Yeni resim eklemek için ekstra bir boş alan
    fields = ('imagePath', 'resizedImage')
    readonly_fields = ('resizedImage',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1  # Yeni yorum eklemek için ekstra bir boş alan
    fields = ('firstName', 'lastName', 'email', 'content', 'approved')
    readonly_fields = ('firstName', 'lastName', 'email', 'content', 'ip')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('categoryName', 'parent', 'site', 'order', 'createdAt', 'updatedAt', 'category_image_preview')
    list_filter = ('site',)
    search_fields = ('categoryName', 'slug', 'categoryDescription')
    prepopulated_fields = {'slug': ('categoryName',)}
    ordering = ('order',)
    readonly_fields = ('category_image_preview',)

    def category_image_preview(self, obj):
        if obj.categoryImage:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.categoryImage.url)
        return "No Image"

    category_image_preview.short_description = "Kategori Görseli Önizleme"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'featured', 'slider', 'active', 'publicationDate', 'counter', 'article_image_preview')
    list_filter = ('site',)
    search_fields = ('title', 'slug', 'content', 'meta', 'metaDescription')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('site', 'counter', 'article_image_preview')
    date_hierarchy = 'publicationDate'
    inlines = [ImageInline, CommentInline]  # Resim ve yorumlar burada ilişkilendiriliyor

    def article_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"

    article_image_preview.short_description = "Makale Resmi Önizleme"


@admin.register(PopupAd)
class PopupAdAdmin(admin.ModelAdmin):
    list_display = ('id', 'isActive', 'createdAt', 'updatedAt')
    list_filter = ('isActive', 'sites')
    search_fields = ('content',)
    filter_horizontal = ('sites',)  # Many-to-Many alanı için yatay seçim arayüzü


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('article', 'imagePath', 'resizedImage', 'createdAt', 'updatedAt')
    search_fields = ('article__title', 'imagePath')
    list_filter = ('article',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'firstName', 'lastName', 'email', 'approved', 'rating', 'ip', 'createdAt')
    list_filter = ('approved', 'rating', 'article')
    search_fields = ('firstName', 'lastName', 'email', 'phoneNumber', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)

    approve_comments.short_description = "Seçilen yorumları onayla"


class VisitorAnalyticsAdmin(admin.ModelAdmin):
    """
    Ziyaretçi İstatistiklerini admin panelinde yönetmek için özelleştirilmiş yapı.
    """

    # Listeleme Ekranındaki Alanlar
    list_display = (
        'site',  # Django'nun varsayılan Site modeli
        'visit_type',
        'article',
        'ip_address',
        'country',
        'city',
        'device_type',
        'operating_system',
        'browser',
        'session_duration',
        'is_bounce',
        'visit_date'
    )

    # Filtreleme Alanları
    list_filter = (
        'site',
        'visit_type',
        'country',
        'city',
        'device_type',
        'operating_system',
        'browser',
        'is_bounce',
        'visit_date'
    )

    # Arama Alanları
    search_fields = (
        'ip_address',
        'country',
        'city',
        'browser',
        'operating_system',
        'article__title',
        'site__domain'  # Django'nun varsayılan Site modeli için domain araması
    )

    # Sadece Görüntülenebilen Alanlar
    readonly_fields = (
        'site',
        'visit_type',
        'article',
        'ip_address',
        'user_agent',
        'referer',
        'visit_date',
        'country',
        'city',
        'device_type',
        'operating_system',
        'browser',
        'session_duration',
        'is_bounce'
    )

    # Alanları Gruplandırma
    fieldsets = (
        ('Site ve Ziyaret Bilgileri', {
            'fields': ('site', 'visit_type', 'article', 'ip_address', 'user_agent', 'referer', 'visit_date')
        }),
        ('Konum ve Cihaz Bilgileri', {
            'fields': ('country', 'city', 'device_type', 'operating_system', 'browser')
        }),
        ('Oturum Detayları', {
            'fields': ('session_duration', 'is_bounce'),
        }),
    )

    def get_queryset(self, request):
        """
        Optimize edilmiş sorgu seti.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('site', 'article')  # İlişkili tablo sorgularını optimize eder.


# Admin paneline kaydetme
admin.site.register(VisitorAnalytics, VisitorAnalyticsAdmin)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    description: Site ile ilgili meta, logo/favicon, renk gibi temel ayarları yönetin.
    """

    list_display = ("id", "siteName", "site", "homeTheme", "updatedAt")
    search_fields = ("siteName", "metaTitle", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("Temel Site Bilgileri", {
            "fields": ("siteName", "metaTitle", "metaDescription", "googleFont", "colors"),
            "description": "Site adı, SEO başlık ve açıklamaları, font ve renk gibi temel özellikler."
        }),
        ("Logo & Favicon", {
            "fields": ("faviconBlack", "faviconWhite", "logoBlack", "logoWhite"),
            "description": (
                "Site için siyah/beyaz favicon ve logoyu yükleyebilirsiniz. "
                "Örnek: Siyah arka planlı favicon, Beyaz arka planlı logo."
            )
        }),
        ("Tema Seçenekleri", {
            "fields": ("homeTheme", "categoryTheme", "articleDetailTheme"),
            "description": (
                "Anasayfa, kategori ve makale detay sayfaları için tema numaralarını seçin. "
                "Örnek: 1, 2 veya 3."
            )
        }),
        ("Politikalar", {
            "fields": ("cookiePolicy", "privacyPolicy", "termsOfUse", "kvkkAgreement"),
            "description": "Çerez Politikası, Gizlilik Politikası, Kullanım Koşulları ve KVKK metinleri."
        }),
        ("İletişim Bilgileri", {
            "fields": ("phone", "gsm", "email", "address", "googleMap"),
            "description": (
                "Telefon, E-posta, Adres, Google Haritalar linki gibi iletişim bilgilerini düzenleyin."
            )
        }),
        ("Hakkımızda", {
            "fields": ("aboutUsTitle", "aboutUsContent", "aboutUsImage"),
            "description": (
                "Hakkımızda sayfasındaki başlık, içerik ve görsel bilgilerini düzenleyin."
            )
        }),
        ("Site Alanı", {
            "fields": ("site",),
            "description": "Bu ayarların ait olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# HomePageSettings Admin
# -----------------------------------------------------------------------------
@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    """
    description: Anasayfada görünmesi planlanan slider, son makaleler sloganı, kayan yazı vb. ayarlar.
    """
    list_display = ("id", "site", "sliderSlogan", "tickerText", "updatedAt")
    search_fields = ("sliderSlogan", "tickerText", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("Giriş Slider", {
            "fields": ("sliderSlogan", "sliderSubText", "sliderButtonText", "sliderButtonLink"),
            "description": (
                "Anasayfada ilk görünen slider bölümündeki slogan, alt metin ve buton ayarları."
            )
        }),
        ("Son Makaleler & Kayan Yazı", {
            "fields": ("lastArticlesSlogan", "tickerText"),
            "description": (
                "Anasayfa üzerinde son makaleler başlığı veya kayan yazı gibi ek metin alanları."
            )
        }),
        ("Alt Bilgi Duyuru", {
            "fields": (
                "footerAnnouncementTitle",
                "footerAnnouncementButtonText",
                "footerAnnouncementButtonLink",
            ),
            "description": "Anasayfanın alt kısmında gösterilecek duyuru başlığı ve buton ayarları."
        }),
        ("Site Alanı", {
            "fields": ("site",),
            "description": "Bu ayarların ait olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# FooterSettings Admin
# -----------------------------------------------------------------------------
@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    """
    description: Footer (alt bilgi) alanındaki metin, duyuru ve yardımcı linkleri düzenlemek için admin arayüzü.
    """
    list_display = ("id", "site", "footerSlogan", "updatedAt")
    search_fields = ("footerSlogan", "footerAnnouncementTitle", "site__domain")
    ordering = ("-updatedAt",)

    fieldsets = (
        ("Footer Sloganı", {
            "fields": ("footerSlogan",),
            "description": "Footer'da kısa bir açıklama veya slogan görüntülemek için kullanılır."
        }),
        ("Footer Duyuru", {
            "fields": (
                "footerAnnouncementTitle",
                "footerAnnouncementButtonText",
                "footerAnnouncementButtonLink",
            ),
            "description": (
                "Footer'da duyuru göstermek istiyorsanız başlık ve buton ayarlarını bu alandan "
                "yapabilirsiniz."
            )
        }),
        ("Yardımcı Linkler", {
            "fields": ("helperLinks",),
            "description": (
                "JSON formatında isim/url tutarak kullanıcıların hızlı erişimi için "
                "yardımcı linkler ekleyebilirsiniz. Örnek: "
                "[{\"name\": \"Hakkımızda\", \"url\": \"/hakkimizda\"}, ...]"
            )
        }),
        ("Footer En Alt Bilgi", {
            "fields": ("footerBottomText",),
            "description": "Footer'ın en alt kısmında gösterilecek (ör. copyright) metni."
        }),
        ("Site Alanı", {
            "fields": ("site",),
            "description": "Bu ayarların ait olduğu site bilgisi."
        }),
    )


# -----------------------------------------------------------------------------
# Menu Admin
# -----------------------------------------------------------------------------
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """
    description: Sitenin menü yapılarını yönetmek için admin arayüzü.
    """
    list_display = ("id", "site", "title", "isMainMenu", "isFeatured", "showCategories", "order", "updatedAt")
    search_fields = ("title", "site__domain")
    ordering = ("order",)

    fieldsets = (
        ("Menü Bilgileri", {
            "fields": ("title", "link"),
            "description": (
                "Menüde gösterilecek başlık ve tıklandığında gidilecek URL/rota bilgisi."
            )
        }),
        ("Ayarlar", {
            "fields": ("isMainMenu", "isFeatured", "showCategories", "order"),
            "description": (
                "Menünün ana menüde gösterilip gösterilmeyeceği, öne çıkarılmış olup olmayacağı, "
                "alt kategorilerin otomatik listelenmesi gibi detaylar."
            )
        }),
        ("Site Alanı", {
            "fields": ("site",),
            "description": "Bu menünün bağlı olduğu site bilgisi."
        }),
    )
