from rest_framework import serializers

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
        read_only_fields = ['id', 'ip', 'createdAt', 'updatedAt']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            'id', 'site', 'article', 'imagePath', 'resizedImage', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'resizedImage', 'createdAt', 'updatedAt']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'site', 'category', 'title', 'content', 'featured', 'slider',
            'active', 'slug', 'counter', 'meta', 'metaDescription',
            'publicationDate', 'image', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'counter', 'createdAt', 'updatedAt', 'publicationDate']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'site', 'categoryName', 'categoryDescription', 'slug',
            'meta', 'metaDescription', 'parent', 'children', 'order',
            'categoryImage', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'children', 'createdAt', 'updatedAt']

    def get_children(self, obj):
        # Alt kategorileri alır
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

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
