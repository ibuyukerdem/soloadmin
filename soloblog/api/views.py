from datetime import datetime, timedelta

from django.contrib.sites.models import Site
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from common.utils import paginate_or_default
from soloblog.models import VisitorAnalytics, Category, Article, Image, Comment, PopupAd, Advertisement
from .serializers import CategorySerializer, ArticleSerializer, ImageSerializer, CommentSerializer, PopupAdSerializer, \
    AdvertisementSerializer, VisitorAnalyticsSerializer


class VisitorAnalyticsViewSet(ModelViewSet):
    """
    Ziyaretçi istatistikleri için CRUD işlemleri:

    - Ziyaretçi kayıtlarını listele.
    - Yeni bir ziyaretçi kaydı oluştur.
    - Ziyaretçi kaydını görüntüle, güncelle veya sil.
    """
    queryset = VisitorAnalytics.objects.order_by('createdAt').all()
    serializer_class = VisitorAnalyticsSerializer

    @swagger_auto_schema(
        operation_description="Site, ziyaret türü veya tarih bazında filtreleme yapmak için parametreleri kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'visit_type', openapi.IN_QUERY,
                description="Ziyaret türüne göre filtreleme ('homepage' veya 'article')", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'start_date', openapi.IN_QUERY, description="Başlangıç tarihi (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY, description="Bitiş tarihi (YYYY-MM-DD)", type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Ziyaretçi kayıtlarını listeleme. Opsiyonel olarak site, ziyaret türü ve tarih aralığına göre filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        visit_type = self.request.query_params.get('visit_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if visit_type:
            queryset = queryset.filter(visit_type=visit_type)
        if start_date and end_date:
            queryset = queryset.filter(visit_date__range=[start_date, end_date])

        # Sayfalama işlemi
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return paginate_or_default(queryset, self.get_serializer_class(), request)

    def destroy(self, request, *args, **kwargs):
        """
        Ziyaretçi kaydını silme işlemi.
        """
        visitor = self.get_object()
        visitor.delete()
        return Response(status=204)


class AdvertisementViewSet(ModelViewSet):
    """
    Reklamlar için CRUD işlemleri:

    - Reklamları listele.
    - Yeni bir reklam oluştur.
    - Reklam detayını görüntüle, güncelle veya sil.
    """
    queryset = Advertisement.objects.order_by('createdAt').all()
    serializer_class = AdvertisementSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir siteye veya reklam alanına göre filtreleme yapmak için parametreleri kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'position', openapi.IN_QUERY, description="Reklam alanına göre filtreleme (örnek: 'sidebar', 'topbar')",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Reklamları listeleme. Opsiyonel olarak site ve alan bazında filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        position = self.request.query_params.get('position')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if position:
            queryset = queryset.filter(position=position)

        return paginate_or_default(queryset, self.get_serializer_class(), request)


class PopupAdViewSet(ModelViewSet):
    """
    Pop-up reklamlar için CRUD işlemleri:

    - Reklamları listele.
    - Yeni bir reklam oluştur.
    - Reklam detayını görüntüle, güncelle veya sil.
    """
    queryset = PopupAd.objects.order_by('createdAt').all()
    serializer_class = PopupAdSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir siteye bağlı reklamları filtrelemek için 'site_id' parametresini kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'is_active', openapi.IN_QUERY, description="Sadece aktif reklamları görmek için",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Reklamları listeleme. Opsiyonel olarak site ve aktif duruma göre filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        is_active = self.request.query_params.get('is_active')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(sites__id=site_id)
        if is_active is not None:
            queryset = queryset.filter(isActive=is_active)

        return paginate_or_default(queryset, self.get_serializer_class(), request)


def apply_filters(queryset, filters):
    """
    Dinamik olarak verilen filtreleri queryset'e uygular.
    :param queryset: Filtrelenecek queryset
    :param filters: Uygulanacak filtrelerin sözlüğü (key: alan adı, value: filtre değeri)
    :return: Filtrelenmiş queryset
    """
    for key, value in filters.items():
        if value is not None:  # Boş olmayan filtreleri uygula
            queryset = queryset.filter(**{key: value})
    return queryset


class CommentViewSet(ModelViewSet):
    """
    Makale yorumları için CRUD işlemleri:

    - Yorumları listele.
    - Yeni bir yorum ekle.
    - Yorum detayını görüntüle, güncelle veya sil.
    """
    queryset = Comment.objects.order_by('createdAt').all()
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir site, makale veya onay durumuna göre yorumları filtrelemek için parametreleri kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'article_id', openapi.IN_QUERY, description="Makale ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'approved', openapi.IN_QUERY, description="Onaylanmış yorumları filtrelemek için",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Yorumları listeleme. Opsiyonel olarak site, makale ve onay durumuna göre filtreleme yapılabilir.
        """
        # Filtreleme için gerekli parametreler
        filters = {
            "site_id": self.request.query_params.get("site_id"),
            "article_id": self.request.query_params.get("article_id"),
            "approved": self.request.query_params.get("approved"),
        }

        # Filtreleri uygula
        queryset = apply_filters(self.get_queryset(), filters)

        # Sayfalama veya tam listeleme
        return paginate_or_default(queryset, self.get_serializer_class(), request)

    def destroy(self, request, *args, **kwargs):
        """
        Yorum silme işlemi.
        """
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(ModelViewSet):
    """
    Makale resimleri için CRUD işlemleri:

    - Resimleri listele.
    - Yeni bir resim yükle.
    - Resim detayını görüntüle, güncelle veya sil.
    """
    queryset = Image.objects.order_by('createdAt').all()
    serializer_class = ImageSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir site veya makaleye ait resimleri filtrelemek için 'site_id' veya 'article_id' parametrelerini kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'article_id', openapi.IN_QUERY, description="Makale ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Resimleri listeleme. Opsiyonel olarak site ve makale bazında filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        article_id = self.request.query_params.get('article_id')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if article_id:
            queryset = queryset.filter(article_id=article_id)

        return paginate_or_default(queryset, self.get_serializer_class(), request)

    def destroy(self, request, *args, **kwargs):
        """
        Resim silme işlemi.
        """
        image = self.get_object()
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleViewSet(ModelViewSet):
    """
    Makaleler için CRUD işlemleri:

    - Makaleleri listele.
    - Yeni bir makale oluştur.
    - Makale detayını görüntüle, güncelle veya sil.
    """
    queryset = Article.objects.select_related('category', 'category__parent', 'site').order_by('createdAt').all()
    serializer_class = ArticleSerializer

    @swagger_auto_schema(
        operation_description="Belirli bir siteye ait makaleleri filtrelemek için 'site_id' parametresini kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'category_id', openapi.IN_QUERY, description="Kategori ID'sine göre filtreleme",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'featured', openapi.IN_QUERY, description="Öne çıkan makaleleri filtrelemek için",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Makaleleri listeleme. Opsiyonel olarak site, kategori ve öne çıkan durumuna göre filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        category_id = self.request.query_params.get('category_id')
        featured = self.request.query_params.get('featured')

        queryset = self.get_queryset()

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if featured is not None:
            queryset = queryset.filter(featured=featured)

        return paginate_or_default(queryset, self.get_serializer_class(), request)

    def destroy(self, request, *args, **kwargs):
        """
        Makale silme işlemi.
        """
        article = self.get_object()
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    """
    Kategoriler için CRUD işlemleri:

    - Tüm kategorileri listele.
    - Yeni kategori oluştur.
    - Kategori detayını görüntüle, güncelle veya sil.
    """
    queryset = Category.objects.select_related('parent').prefetch_related('children').order_by('createdAt').all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        """
        Kategori silme işlemi. Alt kategoriler veya bağlı makaleler varsa hata döner.
        """
        category = self.get_object()
        try:
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Belirli bir siteye ait kategorileri filtrelemek için 'site_id' parametresini kullanabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_id', openapi.IN_QUERY, description="Site ID'sine göre filtreleme", type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Kategorileri listeleme. Opsiyonel olarak site bazında filtreleme yapılabilir.
        """
        site_id = self.request.query_params.get('site_id')
        queryset = self.get_queryset()
        if site_id:
            queryset = queryset.filter(site_id=site_id)

        return paginate_or_default(queryset, self.get_serializer_class(), request)


class SiteDetailedReportAPIView(APIView):
    """
        Bir sitenin belirli bir zaman diliminde ve belirli bir alana göre gruplandırılmış ziyaretçi istatistiklerini sağlar.

        Kullanıcı, aşağıdaki gibi parametrelerle farklı raporlar oluşturabilir:
        - time_frame: 'daily', 'weekly', 'monthly', 'yearly'
        - group_by: 'visit_type', 'country', 'city', 'device_type', 'operating_system', 'browser', 'is_bounce'

        Örnek Kullanımlar:
        1. Günlük cihaz türüne göre rapor:
           GET /sites/1/detailed-report/?time_frame=daily&group_by=device_type

        2. Haftalık ülkelere göre ziyaretçi raporu:
           GET /sites/1/detailed-report/?time_frame=weekly&group_by=country

        3. Aylık şehir bazlı ziyaretçi raporu:
           GET /sites/1/detailed-report/?time_frame=monthly&group_by=city

        4. Yıllık işletim sistemine göre ziyaretçi raporu:
           GET /sites/1/detailed-report/?time_frame=yearly&group_by=operating_system

        5. Günlük tarayıcı türüne göre ziyaretçi raporu:
           GET /sites/1/detailed-report/?time_frame=daily&group_by=browser

        6. Aylık ziyaret tipi (homepage/article) bazında rapor:
           GET /sites/1/detailed-report/?time_frame=monthly&group_by=visit_type

        7. Haftalık bounce durumu (hemen çıkma) bazlı rapor:
           GET /sites/1/detailed-report/?time_frame=weekly&group_by=is_bounce

        8. Günlük ülkelere göre rapor:
           GET /sites/1/detailed-report/?time_frame=daily&group_by=country

        9. Yıllık cihaz türüne göre rapor:
           GET /sites/1/detailed-report/?time_frame=yearly&group_by=device_type

        10. Haftalık tarayıcıya göre ziyaretçi raporu:
            GET /sites/1/detailed-report/?time_frame=weekly&group_by=browser
        """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "time_frame",
                openapi.IN_QUERY,
                description="Raporun zaman dilimi: 'daily', 'weekly', 'monthly', 'yearly'. Varsayılan: 'daily'",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "group_by",
                openapi.IN_QUERY,
                description="Gruplama alanı: 'visit_type', 'country', 'city', 'device_type', 'operating_system', 'browser', 'is_bounce'.",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: "Rapor başarıyla oluşturuldu.", 400: "Geçersiz parametreler."},
    )
    def get(self, request, site_id):

        site = get_object_or_404(Site, id=site_id)
        time_frame = request.query_params.get('time_frame', 'daily')  # 'daily', 'weekly', 'monthly', 'yearly'
        group_by = request.query_params.get('group_by')  # Örneğin 'visit_type', 'country' vb.

        if group_by not in ['visit_type', 'country', 'city', 'device_type', 'operating_system', 'browser', 'is_bounce']:
            return Response({'error': 'Geçersiz group_by parametresi.'}, status=400)

        if time_frame == 'daily':
            date_trunc = TruncDay('visit_date')
        elif time_frame == 'weekly':
            date_trunc = TruncWeek('visit_date')
        elif time_frame == 'monthly':
            date_trunc = TruncMonth('visit_date')
        elif time_frame == 'yearly':
            date_trunc = TruncYear('visit_date')
        else:
            return Response({'error': 'Geçersiz time_frame parametresi.'}, status=400)

        report = VisitorAnalytics.objects.filter(
            site=site
        ).annotate(
            period=date_trunc
        ).values('period', group_by).annotate(
            count=Count('id')
        ).order_by('period')

        return paginate_or_default(report, None, request)


class SiteRefererAPIView(APIView):
    """
    Belirli bir sitenin yönlendirme (referer) kayıtlarını listeler.

    Kullanıcı, başlangıç ve bitiş tarihlerini göndererek, bu tarih aralığında
    en fazla ziyaretçi gönderen URL'leri görebilir.

    Örnek Kullanımlar:

    1. Bir sitenin 2024-12-01 ile 2024-12-05 tarihleri arasındaki referer raporu:
       GET /sites/1/referer-report/?start_date=2024-12-01&end_date=2024-12-05

    2. Bir sitenin 2024-11-01 ile 2024-12-01 tarihleri arasındaki referer raporu:
       GET /sites/2/referer-report/?start_date=2024-11-01&end_date=2024-12-01

    3. Belirli bir gün için referer raporu (örneğin 2024-12-01):
       GET /sites/3/referer-report/?start_date=2024-12-01&end_date=2024-12-01

    4. Eksik tarih gönderilirse hata alır:
       GET /sites/1/referer-report/?start_date=2024-12-01
       Dönen Hata: {"error": "Lütfen başlangıç ve bitiş tarihlerini belirtin."}
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Başlangıç tarihi (YYYY-MM-DD formatında).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="Bitiş tarihi (YYYY-MM-DD formatında).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: "Referer raporu başarıyla oluşturuldu.", 400: "Geçersiz parametreler."},
    )
    def get(self, request, site_id):
        site = get_object_or_404(Site, id=site_id)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'Lütfen başlangıç ve bitiş tarihlerini belirtin.'}, status=400)

        referers = VisitorAnalytics.objects.filter(
            site=site,
            visit_date__range=[start_date, end_date]
        ).values('referer').annotate(
            count=Count('id')
        ).order_by('-count')

        return paginate_or_default(referers, None, request)


class SiteTrafficAPIView(APIView):
    """
    Belirli bir sitenin günlük (son 30 gün) veya aylık (son 6 ay) ziyaretçi trafiğini döner.

    Kullanıcı yalnızca bir parametre gönderebilir: 'daily' veya 'monthly'.

    Örnek Kullanımlar:
    1. Son 30 gün için günlük trafik:
       GET /sites/1/traffic-report/?type=daily

    2. Son 6 ay için aylık trafik:
       GET /sites/1/traffic-report/?type=monthly
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description="Rapor türü: 'daily' (Son 30 gün) veya 'monthly' (Son 6 ay).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: "Başarılı", 400: "Geçersiz parametre veya tür."},
    )
    def get(self, request, site_id):
        # Belirtilen siteyi getir, bulunamazsa 404 döner
        site = get_object_or_404(Site, id=site_id)

        # Kullanıcıdan sorgu tipi al
        traffic_type = request.query_params.get('type')

        if not traffic_type:
            return Response(
                {"error": "Bir tür belirtmek zorundasınız: 'daily' veya 'monthly'."},
                status=400
            )

        if traffic_type not in ['daily', 'monthly']:
            return Response(
                {"error": "Geçersiz tür. Sadece 'daily' veya 'monthly' kabul edilir."},
                status=400
            )

        # Tarih hesaplamaları
        today = datetime.today()

        if traffic_type == 'daily':
            last_30_days = today - timedelta(days=30)

            # Günlük ziyaretçi sayıları
            daily_visitors = VisitorAnalytics.objects.filter(
                site=site,
                visit_date__gte=last_30_days
            ).annotate(
                day=TruncDay('visit_date')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')

            # Dönüş formatı
            formatted_data = [
                {"date": entry["day"].strftime('%Y-%m-%d'), "visitors": entry["count"]} for entry in daily_visitors
            ]

            return paginate_or_default(formatted_data, None, request)

        elif traffic_type == 'monthly':
            last_6_months = today - timedelta(days=180)

            # Aylık ziyaretçi sayıları
            monthly_visitors = VisitorAnalytics.objects.filter(
                site=site,
                visit_date__gte=last_6_months
            ).annotate(
                month=TruncMonth('visit_date')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')

            # Dönüş formatı
            formatted_data = [
                {"date": entry["month"].strftime('%Y-%m-%d'), "visitors": entry["count"]} for entry in monthly_visitors
            ]

            return paginate_or_default(formatted_data, None, request)


class AllSitesVisitorStatsAPIView(APIView):
    """
    Tüm siteler veya belirli bir site için günlük, haftalık, aylık ve yıllık ziyaretçi istatistiklerini döner.

    Kullanıcı, aşağıdaki parametrelerle sorgu yapabilir:
    - `type`: İstatistik türü ('daily', 'weekly', 'monthly', 'yearly').
    - `site_id`: Belirli bir site için sonuç döndürmek üzere site ID'si (opsiyonel).

    Örnek Kullanımlar:
    1. Tüm sitelerin günlük istatistikleri:
       GET /sites/visitor-stats/?type=daily

    2. Belirli bir sitenin günlük istatistikleri (Site ID: 1):
       GET /sites/visitor-stats/?type=daily&site_id=1

    3. Belirli bir sitenin aylık istatistikleri (Site ID: 2):
       GET /sites/visitor-stats/?type=monthly&site_id=2

    4. Tüm sitelerin haftalık istatistikleri:
       GET /sites/visitor-stats/?type=weekly

    5. Parametre olmadan tüm istatistikler:
       GET /sites/visitor-stats/

    Hatalı Kullanımlar:
    1. Geçersiz `type` parametresi:
       GET /sites/visitor-stats/?type=invalid
       Dönen Hata: {"error": "Geçersiz 'type' parametresi. Sadece 'daily', 'weekly', 'monthly', 'yearly' kabul edilir."}

    2. Olmayan bir site ID'si:
       GET /sites/visitor-stats/?site_id=999
       Dönen Hata: {"detail": "Not found."}
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description=(
                        "İstatistik türü: 'daily' (Günlük), 'weekly' (Haftalık), "
                        "'monthly' (Aylık), 'yearly' (Yıllık). Parametre gönderilmezse tüm veriler döner."
                ),
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "site_id",
                openapi.IN_QUERY,
                description="Site ID'sini belirtin. Parametre verilmezse tüm siteler için sonuç döner.",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={200: "Başarılı", 400: "Geçersiz parametre."},
    )
    def get(self, request):
        # Parametreleri al
        stats_type = request.query_params.get('type', None)
        site_id = request.query_params.get('site_id', None)

        # Geçerli 'type' kontrolü
        valid_types = ['daily', 'weekly', 'monthly', 'yearly']
        if stats_type and stats_type not in valid_types:
            return Response(
                {"error": "Geçersiz 'type' parametresi. Sadece 'daily', 'weekly', 'monthly', 'yearly' kabul edilir."},
                status=400)

        # Site filtreleme
        site_filter = {}
        if site_id:
            site = get_object_or_404(Site, id=site_id)
            site_filter['site'] = site

        data = {}

        # Günlük ziyaretçi sayıları
        if not stats_type or stats_type == 'daily':
            daily_visitors = VisitorAnalytics.objects.filter(
                **site_filter
            ).annotate(
                day=TruncDay('visit_date')
            ).values('site__name', 'day').annotate(
                count=Count('id')
            ).order_by('day')
            data['daily_visitors'] = paginate_or_default(daily_visitors, None, request).data

        # Haftalık ziyaretçi sayıları
        if not stats_type or stats_type == 'weekly':
            weekly_visitors = VisitorAnalytics.objects.filter(
                **site_filter
            ).annotate(
                week=TruncWeek('visit_date')
            ).values('site__name', 'week').annotate(
                count=Count('id')
            ).order_by('week')
            data['weekly_visitors'] = paginate_or_default(weekly_visitors, None, request).data

        # Aylık ziyaretçi sayıları
        if not stats_type or stats_type == 'monthly':
            monthly_visitors = VisitorAnalytics.objects.filter(
                **site_filter
            ).annotate(
                month=TruncMonth('visit_date')
            ).values('site__name', 'month').annotate(
                count=Count('id')
            ).order_by('month')
            data['monthly_visitors'] = paginate_or_default(monthly_visitors, None, request).data

        # Yıllık ziyaretçi sayıları
        if not stats_type or stats_type == 'yearly':
            yearly_visitors = VisitorAnalytics.objects.filter(
                **site_filter
            ).annotate(
                year=TruncYear('visit_date')
            ).values('site__name', 'year').annotate(
                count=Count('id')
            ).order_by('year')
            data['yearly_visitors'] = paginate_or_default(yearly_visitors, None, request).data

        return Response(data)
