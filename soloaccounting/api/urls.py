from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet, me, UserSiteViewSet, ProductViewSet, SiteUrunViewSet, UserMenuViewSet, ApplyCampaignView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'usersites', UserSiteViewSet, basename='usersite')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'siteurun', SiteUrunViewSet, basename='siteurun')
router.register(r'user-menu', UserMenuViewSet, basename='user-menu')

urlpatterns = [
    path('me/', me, name='me'),  # Giriş yapan kullanıcı bilgilerini döndüren endpoint
    path('campaigns/apply/', ApplyCampaignView.as_view(), name='apply-campaign'),
]

urlpatterns += router.urls
