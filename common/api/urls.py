from rest_framework.routers import DefaultRouter
from .views import GoogleApplicationsIntegrationViewSet, SiteSettingsViewSet

router = DefaultRouter()
router.register(r'google-integrations', GoogleApplicationsIntegrationViewSet, basename='google-integration')
router.register(r'site-settings', SiteSettingsViewSet, basename='site-settings')


urlpatterns = router.urls
