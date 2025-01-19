"""
views.py

Bu dosya, common.models'taki modeller için DRF ViewSet tanımlarını içerir.
Swagger (drf-yasg) ile birlikte, isteklerin filtrelenmesi ve soyut AbstractBaseViewSet
mirası sağlanır.
"""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from common.base_views import AbstractBaseViewSet
from common.models import (
    LogEntry,
    WhatsAppSettings,
    SmsSettings,
    SmtpSettings,
    GoogleApplicationsIntegration,
    SocialMedia,
)
from .serializers import (
    LogEntrySerializer,
    WhatsAppSettingsSerializer,
    SmsSettingsSerializer,
    SmtpSettingsSerializer,
    GoogleApplicationsIntegrationSerializer,
    SocialMediaSerializer,
    CustomUserSerializer
)


# -----------------------------------------------------------------------------
# LogEntry ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="Log Entry CRUD",
    operation_description="""
LogEntry kaydı için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: model_name, operation, status
<br><b>Arama Yapılabilen Alanlar</b>: user, ip_address, model_name, operation, status
<br><b>Sıralama Yapılabilen Alanlar</b>: timestamp, id, status
""",
    tags=["Log Entry"]
)
class LogEntryViewSet(AbstractBaseViewSet):
    """
    LogEntry kaydı için CRUD işlemleri.
    """
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["model_name", "operation", "status"]
    search_fields = ["user", "ip_address", "model_name", "operation", "status"]
    ordering_fields = ["timestamp", "id", "status"]
    ordering = ["-timestamp"]


# -----------------------------------------------------------------------------
# WhatsAppSettings ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="WhatsApp Settings CRUD",
    operation_description="""
WhatsApp API ayarları için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: apiUrl, phoneNumber
<br><b>Arama Yapılabilen Alanlar</b>: apiUrl, phoneNumber
<br><b>Sıralama Yapılabilen Alanlar</b>: id, kontorMiktari, createdAt
""",
    tags=["WhatsApp Settings"]
)
class WhatsAppSettingsViewSet(AbstractBaseViewSet):
    """
    WhatsApp API ayarları için CRUD işlemleri.
    """
    queryset = WhatsAppSettings.objects.all()
    serializer_class = WhatsAppSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["apiUrl", "phoneNumber"]
    search_fields = ["apiUrl", "phoneNumber"]
    ordering_fields = ["id", "kontorMiktari", "createdAt"]
    ordering = ["-createdAt"]


# -----------------------------------------------------------------------------
# SmsSettings ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="SMS Settings CRUD",
    operation_description="""
SMS API ayarları için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: url, username
<br><b>Arama Yapılabilen Alanlar</b>: url, username
<br><b>Sıralama Yapılabilen Alanlar</b>: id, kontorMiktari, createdAt
""",
    tags=["SMS Settings"]
)
class SmsSettingsViewSet(AbstractBaseViewSet):
    """
    SMS API ayarları için CRUD işlemleri.
    """
    queryset = SmsSettings.objects.all()
    serializer_class = SmsSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["url", "username"]
    search_fields = ["url", "username"]
    ordering_fields = ["id", "kontorMiktari", "createdAt"]
    ordering = ["-createdAt"]


# -----------------------------------------------------------------------------
# SmtpSettings ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="SMTP Settings CRUD",
    operation_description="""
SMTP Ayarları için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: emailAddress, smtpServer
<br><b>Arama Yapılabilen Alanlar</b>: emailAddress, smtpServer
<br><b>Sıralama Yapılabilen Alanlar</b>: id, smtpPort, createdAt
""",
    tags=["SMTP Settings"]
)
class SmtpSettingsViewSet(AbstractBaseViewSet):
    """
    SMTP Ayarları için CRUD işlemleri.
    """
    queryset = SmtpSettings.objects.all()
    serializer_class = SmtpSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["emailAddress", "smtpServer"]
    search_fields = ["emailAddress", "smtpServer"]
    ordering_fields = ["id", "smtpPort", "createdAt"]
    ordering = ["-createdAt"]


# -----------------------------------------------------------------------------
# GoogleApplicationsIntegration ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="Google Applications Integration CRUD",
    operation_description="""
Google Analytics, Tag Manager vb. entegrasyonları için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: applicationType
<br><b>Arama Yapılabilen Alanlar</b>: applicationType
<br><b>Sıralama Yapılabilen Alanlar</b>: id, createdAt
""",
    tags=["Google Applications Integration"]
)
class GoogleApplicationsIntegrationViewSet(AbstractBaseViewSet):
    """
    Google Analytics, Tag Manager vb. entegrasyonları için CRUD işlemleri.
    """
    queryset = GoogleApplicationsIntegration.objects.all()
    serializer_class = GoogleApplicationsIntegrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["applicationType"]
    search_fields = ["applicationType"]
    ordering_fields = ["id", "createdAt"]
    ordering = ["-createdAt"]


# -----------------------------------------------------------------------------
# SocialMedia ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="Social Media CRUD",
    operation_description="""
Sosyal medya ikon & link ayarları için CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: icon
<br><b>Arama Yapılabilen Alanlar</b>: icon, link
<br><b>Sıralama Yapılabilen Alanlar</b>: id, createdAt
""",
    tags=["Social Media"]
)
class SocialMediaViewSet(AbstractBaseViewSet):
    """
    Sosyal medya ikon & link ayarları için CRUD işlemleri.
    """
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["icon"]
    search_fields = ["icon", "link"]
    ordering_fields = ["id", "createdAt"]
    ordering = ["-createdAt"]


# -----------------------------------------------------------------------------
# CustomUser ViewSet
# -----------------------------------------------------------------------------
@swagger_auto_schema(
    operation_summary="Custom User CRUD",
    operation_description="""
CustomUser (genişletilmiş Django User) üzerinde CRUD işlemleri.
<br><b>Filtrelenebilen Alanlar</b>: username, email, isDealer
<br><b>Arama Yapılabilen Alanlar</b>: username, email, phoneNumber
<br><b>Sıralama Yapılabilen Alanlar</b>: id, date_joined
""",
    tags=["Custom User"]
)
class CustomUserViewSet(viewsets.ModelViewSet):
    """
    CustomUser (genişletilmiş Django User) üzerinde CRUD işlemleri.
    Burada AbstractBaseViewSet yerine kendi güvenlik/filtre yaklaşımınızı tanımlayabilirsiniz.
    Örnek olarak sadece is_staff olan erişsin vb.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = get_user_model().objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["username", "email", "isDealer"]
    search_fields = ["username", "email", "phoneNumber"]
    ordering_fields = ["id", "date_joined"]
    ordering = ["-date_joined"]
