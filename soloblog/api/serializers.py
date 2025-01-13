from django.utils.formats import date_format
from rest_framework import serializers

from common.base_serializer import BaseOnlyDateSerializer
from soloblog.models import Category, Article, Image, Comment, PopupAd, Advertisement, VisitorAnalytics


class VisitorAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorAnalytics
        fields = [
            'id', 'site', 'visit_type', 'article', 'ip_address', 'user_agent', 'referer',
            'visit_date', 'country', 'city', 'device_type', 'operating_system',
            'browser', 'session_duration', 'is_bounce', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'is_bounce', 'createdAt', 'updatedAt']


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            'id', 'site', 'position', 'image', 'link', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class PopupAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopupAd
        fields = [
            'id', 'content', 'sites', 'isActive', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'site', 'article', 'approved', 'firstName', 'lastName',
            'email', 'phoneNumber', 'rating', 'content', 'ip', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'ip', 'createdAt', 'updatedAt', 'site']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            'id', 'site', 'article', 'imagePath', 'resizedImage', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'resizedImage', 'createdAt', 'updatedAt']


class ChildCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'categoryName', 'slug']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    children = ChildCategorySerializer(many=True, read_only=True)
    parent = ChildCategorySerializer(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'site', 'categoryName', 'categoryDescription', 'slug',
            'meta', 'metaDescription', 'parent', 'children', 'order',
            'categoryImage', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'children', 'createdAt', 'updatedAt', 'site']


class ArticleSerializer(BaseOnlyDateSerializer):
    category_name = serializers.CharField(source='category.categoryName', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'site', 'category', 'category_name', 'category_slug', 'title', 'content',
            'featured', 'slider', 'active', 'slug', 'counter', 'meta', 'metaDescription',
            'publicationDate', 'image', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'counter', 'createdAt', 'updatedAt', 'publicationDate', 'site']

    # Örnek: Alan bazlı validasyon
    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Başlık en az 10 karakter olmalıdır.")
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("İçerik boş olamaz.")
        return value

    # Örnek: Genel validasyon (non_field_errors) - birden fazla alan ilişkiliyse
    def validate(self, attrs):
        publication_date = attrs.get('publicationDate')
        if publication_date:
            from datetime import datetime
            if publication_date < datetime.now().date():
                # Örneğin, bugünün tarihinden küçük ise hata ver
                raise serializers.ValidationError({
                    'publicationDate': ["Yayın tarihi geçmiş bir tarih olamaz."]
                })
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'publicationDate' in representation and representation['publicationDate'] is not None:
            publication_date_value = instance.publicationDate
            # Tarihi Python ile elle formatla (gün ve ay 2 basamak olacak)
            #representation['publicationDate'] = publication_date_value.strftime('%d.%m.%Y')
            representation['publicationDate'] = publication_date_value.isoformat()
        return representation


class SiteDetailedReportSerializer(serializers.Serializer):
    period = serializers.DateTimeField()
    group_by = serializers.CharField()
    count = serializers.IntegerField()
    optional_field = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        fields = ['period', 'group_by', 'count']


class SiteRefererSerializer(serializers.Serializer):
    referer = serializers.URLField()
    count = serializers.IntegerField()
    optional_field = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        fields = ['referer', 'count']


class DailyVisitorSerializer(serializers.Serializer):
    site__name = serializers.CharField()
    day = serializers.DateField()
    count = serializers.IntegerField()


class WeeklyVisitorSerializer(serializers.Serializer):
    site__name = serializers.CharField()
    week = serializers.DateField()
    count = serializers.IntegerField()


class MonthlyVisitorSerializer(serializers.Serializer):
    site__name = serializers.CharField()
    month = serializers.DateField()
    count = serializers.IntegerField()


class YearlyVisitorSerializer(serializers.Serializer):
    site__name = serializers.CharField()
    year = serializers.DateField()
    count = serializers.IntegerField()


class AllSitesVisitorStatsSerializer(serializers.Serializer):
    daily_visitors = DailyVisitorSerializer(many=True)
    weekly_visitors = WeeklyVisitorSerializer(many=True)
    monthly_visitors = MonthlyVisitorSerializer(many=True)
    yearly_visitors = YearlyVisitorSerializer(many=True)
