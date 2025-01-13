# solopayment/api/views.py

"""
Bu dosya, DRF view set tanımlarını içerir. Swagger ile otomatik dokümantasyon,
filtreleme, arama ve sıralama örnekleri eklenmiştir.

Kullanılan kütüphaneler:
- drf-yasg: Swagger dokümantasyonunu eklemek için
- django-filter: Filtreleme için
- rest_framework.filters (SearchFilter, OrderingFilter): Arama ve sıralama
"""

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

from common.base_views import AbstractBaseViewSet, log_action
from solopayment.models import (
    PaymentProvider,
    PaymentMethod,
    PaymentFee,
    PaymentTransaction
)
from .serializers import (
    PaymentProviderSerializer,
    PaymentMethodSerializer,
    PaymentFeeSerializer,
    PaymentTransactionSerializer
)


# ------------------------------------------------------------------------
# PaymentProviderViewSet
# PaymentProvider modeli AbstractBaseModel'den miras almadığı için
# doğrudan ModelViewSet kullanır.
# ------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="List all Payment Providers. "
                          "Filtreleme: ?isActive=true/false, Arama: ?search=Name, "
                          "Sıralama: ?ordering=providerName,-createDate vb.",
    tags=["PaymentProvider"]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Retrieve a specific Payment Provider by ID.",
    tags=["PaymentProvider"]
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Create a new Payment Provider. "
                          "Tüm siteler için ortaktır, site alanı yoktur.",
    tags=["PaymentProvider"]
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Update a Payment Provider (full update).",
    tags=["PaymentProvider"]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Partial update for a Payment Provider.",
    tags=["PaymentProvider"]
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Delete a Payment Provider by ID.",
    tags=["PaymentProvider"]
))
class PaymentProviderViewSet(ModelViewSet):
    """
    PaymentProvider: Tüm siteler tarafından ortak kullanılan ödeme sağlayıcıları yönetir.
    Filtreleme, arama, sıralama örnekleri eklenmiştir.
    """
    queryset = PaymentProvider.objects.all()
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticated]

    # django-filter ve rest_framework.filters ile filtre/arama/sıralama yapısı
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['isActive']  # ?isActive=true
    search_fields = ['providerName', 'providerCode', 'description']  # ?search=paytr
    ordering_fields = ['createDate', 'updateDate', 'providerName']   # ?ordering=-createDate

    def get_queryset(self):
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="CREATE",
            data=request.data,
            site=None  # PaymentProvider site bazlı değil
        )
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="UPDATE",
            data=request.data,
            site=None
        )
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="DELETE",
            data={"id": instance.id},
            site=None
        )
        return response


# ------------------------------------------------------------------------
# PaymentMethodViewSet
# AbstractBaseModel'den miras aldığı için AbstractBaseViewSet kullanır.
# ------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="List all Payment Methods filtered by user's selected site. "
                          "Ayrıca ?isActive=true, ?search=... gibi parametreler.",
    tags=["PaymentMethod"]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Retrieve a specific Payment Method by ID (site-based).",
    tags=["PaymentMethod"]
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Create a new Payment Method for the user's selected site.",
    tags=["PaymentMethod"]
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Full update of a Payment Method.",
    tags=["PaymentMethod"]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Partial update of a Payment Method.",
    tags=["PaymentMethod"]
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Delete a Payment Method by ID.",
    tags=["PaymentMethod"]
))
class PaymentMethodViewSet(AbstractBaseViewSet):
    """
    PaymentMethod: Bir merchantUser'ın (işletme) belirli bir PaymentProvider ile
    site bazında ilişkilendirdiği ödeme ayarlarını yönetir.
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['isActive', 'commissionPayer', 'defaultForSingleShot']
    search_fields = ['merchantUser__username', 'paymentProvider__providerName', 'credentials']
    ordering_fields = ['createdAt', 'updatedAt', 'merchantUser']


# ------------------------------------------------------------------------
# PaymentFeeViewSet
# AbstractBaseModel + AbstractBaseViewSet
# ------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="List all Payment Fees (site-based). "
                          "Filtreleme örn: ?installmentCount=1, ?isActive=true.",
    tags=["PaymentFee"]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Retrieve a Payment Fee by ID.",
    tags=["PaymentFee"]
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Create a new Payment Fee (taksit/sabit komisyon) for the user's selected site.",
    tags=["PaymentFee"]
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Full update of a Payment Fee.",
    tags=["PaymentFee"]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Partial update of a Payment Fee.",
    tags=["PaymentFee"]
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Delete a Payment Fee by ID.",
    tags=["PaymentFee"]
))
class PaymentFeeViewSet(AbstractBaseViewSet):
    """
    PaymentFee: Taksit veya peşin işlemler için sabit/yüzdesel komisyon tanımları.
    """
    queryset = PaymentFee.objects.all()
    serializer_class = PaymentFeeSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['isActive', 'installmentCount']
    search_fields = ['paymentMethod__paymentProvider__providerName']
    ordering_fields = ['createdAt', 'updatedAt', 'installmentCount']


# ------------------------------------------------------------------------
# PaymentTransactionViewSet
# AbstractBaseModel + AbstractBaseViewSet
# ------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="List Payment Transactions for user's selected site. "
                          "Örnek filtreler: ?status=approved, ?search=payerName",
    tags=["PaymentTransaction"]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Retrieve a single Payment Transaction by ID (site-based).",
    tags=["PaymentTransaction"]
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Create a new Payment Transaction. "
                          "Misafir ödemeler için payerName doldurulabilir.",
    tags=["PaymentTransaction"]
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Full update of a Payment Transaction.",
    tags=["PaymentTransaction"]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Partial update of a Payment Transaction.",
    tags=["PaymentTransaction"]
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Delete a Payment Transaction by ID.",
    tags=["PaymentTransaction"]
))
class PaymentTransactionViewSet(AbstractBaseViewSet):
    """
    PaymentTransaction: Gerçekleşen ödeme işlemlerinin kaydı.
    Site, kullanıcı (veya misafir) bilgileri, tutar, komisyon vb. içerir.
    """
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'installmentCount', 'merchantUser']
    search_fields = ['payerName', 'referenceCode', 'merchantUser__username']
    ordering_fields = ['createdAt', 'updatedAt', 'amount', 'totalPaidAmount']
