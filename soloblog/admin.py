from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Article, Image, Comment, PopupAd, Advertisement, VisitorAnalytics


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
    list_filter = ('parent', 'site')
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
    list_filter = ('featured', 'slider', 'active', 'category')
    search_fields = ('title', 'slug', 'content', 'meta', 'metaDescription')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('counter', 'article_image_preview')
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


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('site', 'position', 'createdAt', 'updatedAt')
    list_filter = ('site', 'position')
    search_fields = ('site__domain', 'position')
    readonly_fields = ('createdAt', 'updatedAt')
    ordering = ('site', 'position')

    fieldsets = (
        (None, {
            'fields': ('site', 'position', 'image', 'link')
        }),
        ('Tarih Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VisitorAnalytics)
class VisitorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('site', 'visit_type', 'article', 'visit_date', 'ip_address', 'session_duration', 'is_bounce')
    list_filter = ('site', 'visit_type', 'is_bounce')
    search_fields = ('site__domain', 'article__title', 'ip_address')
    readonly_fields = ('visit_date', 'createdAt', 'updatedAt')
    ordering = ('-visit_date',)

    def changelist_view(self, request, extra_context=None):
        # Gruplanmış ziyaretçi verilerini almak
        grouped_data = VisitorAnalytics.objects.values('site__domain', 'visit_type').annotate(
            visit_count=Count('id')
        ).order_by('site__domain', 'visit_type')

        # Kurumsal çizelgeyi oluşturmak
        table_html = "<table style='width: 100%; border-collapse: collapse;'>"
        table_html += "<thead><tr><th style='border: 1px solid #ddd; padding: 8px;'>Site</th>"
        table_html += "<th style='border: 1px solid #ddd; padding: 8px;'>Ziyaret Tipi</th>"
        table_html += "<th style='border: 1px solid #ddd; padding: 8px;'>Ziyaret Sayısı</th></tr></thead><tbody>"

        for data in grouped_data:
            table_html += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{data['site__domain']}</td>"
            table_html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{dict(VisitorAnalytics.VISIT_TYPE_CHOICES).get(data['visit_type'])}</td>"
            table_html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{data['visit_count']}</td></tr>"

        table_html += "</tbody></table>"

        extra_context = extra_context or {}
        extra_context['grouped_data'] = format_html(table_html)

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('site', 'article')
