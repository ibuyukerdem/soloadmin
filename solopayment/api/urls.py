# -----------------------------------------------------------------------------
# solopayment/api/urls.py
# -----------------------------------------------------------------------------
"""
Bu dosya, DRF router aracılığıyla endpoint'leri tanımlar.

Örnek:
GET /api/payment-provider/
POST /api/payment-provider/
GET /api/payment-method/
... vb.

İhtiyacınıza göre /api/v1 veya /api/solopayment/... gibi prefiksler 
'project/urls.py' içinde tanımlanabilir.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentProviderViewSet,
    PaymentMethodViewSet,
    PaymentFeeViewSet,
    PaymentTransactionViewSet
)

router = DefaultRouter()
router.register(r'payment-provider', PaymentProviderViewSet, basename='payment-provider')
router.register(r'payment-method', PaymentMethodViewSet, basename='payment-method')
router.register(r'payment-fee', PaymentFeeViewSet, basename='payment-fee')
router.register(r'payment-transaction', PaymentTransactionViewSet, basename='payment-transaction')

urlpatterns = [
    path('', include(router.urls)),
]