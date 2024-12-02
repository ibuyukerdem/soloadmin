from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet, me

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('me/', me, name='me'),  # Giriş yapan kullanıcı bilgilerini döndüren endpoint
]

urlpatterns += router.urls

