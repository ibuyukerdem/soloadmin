from decimal import Decimal
from django.db import models
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from soloaccounting.models import SiteUrun, Menu
from accounts.models import UserSite

from common.models import CustomUser
from soloaccounting.models import Product
from soloaccounting.campaigns.models import Campaign

from .serializers import UserSummarySerializer, UserDetailSerializer, CustomUserSerializer, UserSiteSerializer, \
    ProductSerializer, SiteUrunSerializer, MenuSerializer, ApplyCampaignSerializer
from django.db.models import Q
from django.utils.timezone import now


class ApplyCampaignView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ApplyCampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        user_id = serializer.validated_data.get('user_id', None)
        cart_total = serializer.validated_data.get('cart_total', Decimal('0.00'))

        # Ürünü al
        try:
            product = Product.objects.get(id=product_id, isActive=True)
        except Product.DoesNotExist:
            return Response({'error': 'Ürün bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

        # Kullanıcı bilgisi ve segmentini al (eğer user_id varsa)
        user = None
        user_segment = None
        dealer_segment = None
        is_dealer = False
        if user_id:
            user = CustomUser.objects.get(id=user_id)
            user_segment = user.usersegment_set.first()  # Örnek olarak ilk segment
            dealer_segment = user.dealer_segment
            is_dealer = user.isDealer

        # Şimdi geçerli kampanyaları bul
        now = timezone.now()
        applicable_campaigns = Campaign.objects.filter(
            is_active=True
        ).filter(
            # Başlangıç ve bitiş tarihine göre filtre
            start_date__lte=now,
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        )

        # Ürüne özgü kampanyalar veya tüm ürünlere geçerli kampanyalar
        applicable_campaigns = applicable_campaigns.filter(
            models.Q(products__isnull=True) | models.Q(products=product)
        ).distinct()

        # Kampanyaların koşullarını değerlendir
        # Her kampanya için Condition'ları kontrol et
        eligible_campaigns = []
        for camp in applicable_campaigns:
            conditions = camp.conditions.all()
            if all(self.check_condition(cond, product, user, user_segment, dealer_segment, cart_total) for cond in
                   conditions):
                eligible_campaigns.append(camp)

        # Eğer birden fazla kampanya uygunsa, öncelik belirlemek veya tüm aksiyonları uygulamak gerekebilir.
        # Burada örnek olarak tüm uygun kampanyaların aksiyonlarını uyguluyoruz.
        final_price = product.price
        for camp in eligible_campaigns:
            actions = camp.actions.all()
            for action in actions:
                final_price = self.apply_action(action, final_price, product)

        return Response({
            'product_id': product_id,
            'original_price': str(product.price),
            'discounted_price': str(final_price),
            'campaigns_applied': [c.name for c in eligible_campaigns]
        }, status=200)

    def check_condition(self, condition, product, user, user_segment, dealer_segment, cart_total):
        # Burada condition_type'a göre koşulları kontrol edebilirsiniz.
        ctype = condition.condition_type.code
        params = condition.params

        if ctype == 'USER_SEGMENT':
            # Kullanıcının segmenti condition.user_segment ile eşleşmeli
            if condition.user_segment and user_segment:
                return condition.user_segment == user_segment
            return False

        if ctype == 'DEALER_SEGMENT':
            if condition.dealer_segment and dealer_segment:
                return condition.dealer_segment == dealer_segment
            return False

        if ctype == 'PRODUCT_PURCHASED':
            # Örneğin params={'product_id': X} gibi bir kontrol yapabilirsiniz
            required_pid = params.get('product_id', None)
            # Bu örnekte, koşul "Sepete eklenen ürün bu mu?" olabilir:
            return required_pid == product.id

        if ctype == 'MIN_CART_TOTAL':
            required_amount = Decimal(params.get('amount', '0.00'))
            return cart_total >= required_amount

        # Diğer koşulları da benzer şekilde ekleyin.
        return True

    def apply_action(self, action, current_price, product):
        # Aksiyon tipine göre fiyatı güncelle
        atype = action.action_type.code
        params = action.params

        if atype == 'DISCOUNT_PERCENT':
            percentage = Decimal(params.get('percentage', '0'))
            discount_amount = current_price * (percentage / Decimal('100'))
            return current_price - discount_amount

        if atype == 'DISCOUNT_FIXED':
            discount_value = Decimal(params.get('value', '0.00'))
            return max(current_price - discount_value, Decimal('0.00'))

        # GIFT_PRODUCT ya da ADD_CONTENT gibi aksiyonlar sepete ek nesne eklemek için kullanılabilir.
        # Fiyata direkt etkisi yoksa current_price geri döndürün.
        return current_price


class UserSiteViewSet(viewsets.ModelViewSet):
    """
    Kullanıcı-Site eşleşmeleri CRUD işlemleri için ViewSet.
    """
    queryset = UserSite.objects \
        .select_related('site', 'site__extended_site') \
        .prefetch_related('site__urunSite__urun').order_by('-site__extended_site__isDefault')  # Ürünleri önbelleğe al
    serializer_class = UserSiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user', 'site__extended_site__isDefault', 'site__extended_site__isActive']
    search_fields = ['site__domain', 'user__username']

    user_param = openapi.Parameter(
        'user', openapi.IN_QUERY, description="Filtrelenecek kullanıcı ID'si", type=openapi.TYPE_INTEGER
    )
    is_default_param = openapi.Parameter(
        'site__extended_site__isDefault',
        openapi.IN_QUERY,
        description="Varsayılan site (True/False)",
        type=openapi.TYPE_BOOLEAN,
    )
    is_active_param = openapi.Parameter(
        'site__extended_site__isActive',
        openapi.IN_QUERY,
        description="Aktif site (True/False)",
        type=openapi.TYPE_BOOLEAN,
    )
    search_param = openapi.Parameter(
        'search',
        openapi.IN_QUERY,
        description="Site domain veya kullanıcı adı arama",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        operation_description="Tüm Kullanıcı-Site ilişkilerini listeler.",
        manual_parameters=[user_param, is_default_param, is_active_param, search_param],
        responses={200: UserSiteSerializer(many=True)},
        tags=["Kullanıcı-Site İlişkileri"],
    )
    def list(self, request, *args, **kwargs):
        """
        Swagger için list işlemi açıklaması.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Kullanıcı-Site ilişki kaydı oluşturur.",
        request_body=UserSiteSerializer,
        responses={201: UserSiteSerializer, 400: "Geçersiz veri"},
        tags=["Kullanıcı-Site İlişkileri"],
    )
    def create(self, request, *args, **kwargs):
        """
        Swagger için create işlemi açıklaması.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir Kullanıcı-Site ilişkisini günceller.",
        request_body=UserSiteSerializer,
        responses={200: UserSiteSerializer, 400: "Geçersiz veri"},
        tags=["Kullanıcı-Site İlişkileri"],
    )
    def update(self, request, *args, **kwargs):
        """
        Swagger için update işlemi açıklaması.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir Kullanıcı-Site ilişki kaydını siler.",
        responses={204: "Başarılı silme işlemi"},
        tags=["Kullanıcı-Site İlişkileri"],
    )
    def destroy(self, request, *args, **kwargs):
        """
        Swagger için destroy işlemi açıklaması.
        """
        return super().destroy(request, *args, **kwargs)



class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['id', 'username', 'email', 'isIndividual']  # Filtrelemek istediğiniz alanlar
    search_fields = ['username', 'email']  # Arama için kullanılacak alanlar
    ordering_fields = ['id', 'username', 'email']  # Sıralama için kullanılacak alanlar
    ordering = ['id']  # Varsayılan sıralama

    def get_serializer_class(self):
        """
        Özet veya detay serializer'ı seçmek için `action`'a bağlı bir yapı.
        """
        if self.action == 'list':
            return UserSummarySerializer
        return UserDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user  # Giriş yapan kullanıcı
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(isActive=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['isActive', 'createDate', 'updateDate', 'slug']
    search_fields = ['name', 'slug']

    @swagger_auto_schema(
        operation_summary="Ürünleri Listele",
        operation_description=(
                "Sistemdeki tüm ürünleri listeleyin. Site ID'sine, aktiflik durumuna, oluşturulma ve güncellenme tarihine göre "
                "filtreleme yapabilirsiniz. Ayrıca ürün adı ve slug üzerinden arama yapabilirsiniz."
        ),
        manual_parameters=[
            openapi.Parameter(
                'site',
                openapi.IN_QUERY,
                description="Site ID'sine göre filtreleme yapar.",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'isActive',
                openapi.IN_QUERY,
                description="Ürünün aktiflik durumuna göre filtreleme yapar. (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'createDate',
                openapi.IN_QUERY,
                description="Oluşturulma tarihine göre filtreleme yapar (format: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                'updateDate',
                openapi.IN_QUERY,
                description="Güncellenme tarihine göre filtreleme yapar (format: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                'slug',
                openapi.IN_QUERY,
                description="Ürünün slug değeri üzerinden filtreleme yapar.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Ürün adı veya slug içinde geçen ifadeye göre arama yapar.",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Ürünleri Listeleme İşlemi
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Ürün Detayı Getir",
        operation_description="Belirli bir ürünün detaylarını ID'sine veya slug değerine göre getirir."
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Ürün Detayı Getirme İşlemi
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Yeni Ürün Ekle",
        operation_description="Sisteme yeni bir ürün ekler.",
    )
    def create(self, request, *args, **kwargs):
        """
        Yeni Ürün Ekleme İşlemi
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Ürün Güncelle",
        operation_description="Mevcut bir ürünün tüm detaylarını ID'sine veya slug değerine göre günceller. Bu işlem tüm alanların gönderilmesini gerektirir.",
    )
    def update(self, request, *args, **kwargs):
        """
        Ürün Güncelleme İşlemi (PUT)
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Ürün Bilgilerini Güncelle (Kısmi Güncelleme)",
        operation_description="Mevcut bir ürünün sadece belirli alanlarını günceller. Bu işlem yalnızca güncellenecek alanların gönderilmesini gerektirir.",
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Ürün Kısmi Güncelleme İşlemi (PATCH)
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Ürün Sil",
        operation_description="Belirli bir ürünü ID'sine veya slug değerine göre siler.",
    )
    def destroy(self, request, *args, **kwargs):
        """
        Ürün Silme İşlemi
        """
        return super().destroy(request, *args, **kwargs)


class SiteUrunViewSet(ModelViewSet):
    serializer_class = SiteUrunSerializer

    def get_queryset(self):
        queryset = SiteUrun.objects.all()
        site_user = self.request.query_params.get('site_user')

        if site_user:
            # İlişkili Site ve User filtreleme
            queryset = queryset.filter(site__in=Site.objects.filter(user_id=site_user))

        return queryset

    @swagger_auto_schema(
        operation_summary="Site ve Ürün Eşleşmelerini Listele",
        operation_description="Tüm site ve ürün eşleşmelerini listeleyin. Kullanıcı ID'sine (User ID) göre filtreleme ve ürün adına göre arama yapabilirsiniz.",
        manual_parameters=[
            openapi.Parameter(
                'site_user',
                openapi.IN_QUERY,
                description="Kullanıcı ID'sine (User ID) göre filtreleme yapar.",
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Site ve Ürün Eşleşmelerini Listeleme İşlemi
        """
        return super().list(request, *args, **kwargs)


def transform_menu_data(menu_data, subheader_title, user):
    # menu_data: serializer.data çıktısı
    if not menu_data or not isinstance(menu_data, list):
        return []

    return [
        {
            'subheader': subheader_title,
            'items': [transform_item(m, user) for m in menu_data],
        }
    ]


def transform_item(menu, user):
    if not user.is_superuser and menu.get('is_superuser_only', False):
        return None

    # Alt menüler (children) varsa dönüşüme tabi tut
    children_data = menu.get('children', None)
    if children_data:
        # children_data var ve boş değilse dönüştür
        transformed_children = [transform_item(child, user) for child in children_data if child]
        # Filtreleyip None değerlerini çıkar
        transformed_children = [child for child in transformed_children if child is not None]
    else:
        transformed_children = None

    item = {
        'title': menu['title'],
        'path': menu.get('path'),
        'icon': menu.get('icon'),
        'caption': menu.get('caption'),
        'roles': menu.get('roles'),
        'info': menu.get('info'),
        'disabled': menu.get('disabled'),
        'external': menu.get('external')
    }

    # Eğer children varsa ekle, yoksa hiç ekleme
    if transformed_children:
        item['children'] = transformed_children

    return item


class UserMenuViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MenuSerializer
    queryset = Menu.objects.none()  # list metodu override edilecek

    def get_user_products(self, user):
        """
        Kullanıcının erişebildiği ürünleri alır.
        """
        user_sites = (UserSite.objects
                      .filter(user=user)
                      .select_related('site')
                      .prefetch_related('site__urunSite__urun'))
        all_products = set()
        for us in user_sites:
            if hasattr(us.site, 'urunSite'):
                all_products.update(us.site.urunSite.urun.all())
        return all_products

    @swagger_auto_schema(
        operation_summary="Kullanıcı Menüsünü Listele",
        operation_description="""
        Bu API, kullanıcının erişim yetkisine sahip olduğu menüleri `navData` formatında döndürür.
        Eğer kullanıcı süper kullanıcıysa, sadece süper kullanıcıya özel menüler de dönecektir.
        """,
        responses={
            200: openapi.Response(
                description="Kullanıcı menüsü (navData formatında)",
                schema=MenuSerializer(many=True)
            ),
            401: openapi.Response(
                description="Yetkisiz erişim - kullanıcı giriş yapmamış"
            )
        }
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"user_menu_{user.id}"

        # Cache kontrolü
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        # Kullanıcı ürünlerini al
        user_products = self.get_user_products(user)
        if not user_products:
            empty_nav = []
            cache.set(cache_key, empty_nav, 60 * 5)  # Cache boş verilerle güncellenir
            return Response(empty_nav)

        # Menüler için filtreleme
        menus = Menu.objects.filter(
            product__in=user_products,
            parent__isnull=True
        ).distinct()

        # Süper kullanıcı olmayanlar için `is_superuser_only` filtreleme
        if not user.is_superuser:
            menus = menus.filter(is_superuser_only=False)

        # Menüleri serialize et
        serializer = self.get_serializer(menus, many=True)
        data = serializer.data

        # Menüleri `navData` formatına dönüştür
        nav_data = transform_menu_data(data, "Ürün/Hizmetler", user)

        # Cache'e kaydet ve yanıtla
        cache.set(cache_key, nav_data, 60 * 5)
        return Response(nav_data)


class SiteInfoView(APIView):
    def get(self, request):
        """
        Bu endpoint, gelen isteğin domainine göre Site nesnesini döner.
        Örn. /api/site-info
        """
        if request.site:
            return Response({
                'domain': request.site.domain,
                'site_name': request.site.name,
                'site_id': request.site.id,
            })
        else:
            return Response({
                'error': 'Site not found for this domain.'
            }, status=404)