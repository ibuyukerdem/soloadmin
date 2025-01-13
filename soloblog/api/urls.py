from django.urls import path, include  # 'include' eklendi
from rest_framework.routers import DefaultRouter

from soloblog.api.views import SiteDetailedReportAPIView, SiteRefererAPIView, SiteTrafficAPIView, \
    AllSitesVisitorStatsAPIView, CategoryViewSet, ArticleViewSet, ImageViewSet, CommentViewSet, PopupAdViewSet, \
    AdvertisementViewSet, VisitorAnalyticsViewSet

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'article', ArticleViewSet, basename='article')
router.register(r'image', ImageViewSet, basename='image')
router.register(r'comment', CommentViewSet, basename='comment')
router.register(r'popupad', PopupAdViewSet, basename='popup-ad')
router.register(r'advertisement', AdvertisementViewSet, basename='advertisement')
router.register(r'visitor-analytic', VisitorAnalyticsViewSet, basename='visitor-analytics')
# URL Patterns
urlpatterns = [
    path('', include(router.urls)),
    path('sites/<int:site_id>/detailed-report/', SiteDetailedReportAPIView.as_view(), name='site_detailed_report'),
    path('sites/<int:site_id>/referer-report/', SiteRefererAPIView.as_view(), name='site_referer_report'),
    path('sites/<int:site_id>/traffic-report/', SiteTrafficAPIView.as_view(), name='site_traffic_report'),
    path('sites/visitor-stats/', AllSitesVisitorStatsAPIView.as_view(), name='all_sites_visitor_stats'),
]
