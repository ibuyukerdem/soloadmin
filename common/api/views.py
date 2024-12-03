from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from common.models import GoogleApplicationsIntegration, SiteSettings
from .serializers import GoogleApplicationsIntegrationSerializer, SiteSettingsSerializer

class SiteSettingsViewSet(ModelViewSet):
    """
    Site ayarları için CRUD işlemleri:

    - Site ayarlarını listele.
    - Yeni bir site ayarı ekle.
    - Mevcut bir site ayarını görüntüle, güncelle veya sil.
    """
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir siteye ait ayarları filtrelemek için 'site_id' parametresini kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Site ayarlarını listeleme. Opsiyonel olarak siteye göre filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Site ayarlarını silme işlemi.
        """
        settings = self.get_object()
        settings.delete()
        return Response(status=204)

class GoogleApplicationsIntegrationViewSet(ModelViewSet):
    """
    Google uygulamaları entegrasyonları için CRUD işlemleri:

    - Entegrasyonları listele.
    - Yeni bir entegrasyon oluştur.
    - Entegrasyon detayını görüntüle, güncelle veya sil.
    """
    queryset = GoogleApplicationsIntegration.objects.all()
    serializer_class = GoogleApplicationsIntegrationSerializer

    @swagger_auto_schema(
        operation_description="Site ve uygulama türüne göre filtreleme yapmak için parametreleri kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'application_type', openapi.IN_QUERY, description="Uygulama türüne göre filtreleme (örnek: 'google_analytics', 'google_adsense')", type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Entegrasyonları listeleme. Opsiyonel olarak site ve uygulama türüne göre filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        application_type = self.request.query_params.get('application_type')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if application_type:
            queryset = queryset.filter(applicationType=application_type)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Entegrasyon silme işlemi.
        """
        integration = self.get_object()
        integration.delete()
        return Response(status=204)
