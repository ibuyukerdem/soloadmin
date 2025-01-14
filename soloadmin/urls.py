# soloadmin/urls.py
from .admin import solo_admin_site
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from accounts.views import CustomTokenObtainPairView

#
# 1) Özel permission: Sadece staff kullanıcı görebilsin
#
from rest_framework.permissions import BasePermission

class OnlyStaffCanSeeDocs(BasePermission):
    """
    Dokümantasyonu yalnızca staff (is_staff=True) kullanıcılar görüntüleyebilir.
    Hata alırsanız 401 Unauthorized döner.
    """
    message = "Bu dokümantasyonu yalnızca staff kullanıcılar görüntüleyebilir."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )

#
# 2) Her app için ayrı schema_view
#    patterns parametresi sayesinde ilgili app urls'ine göre ayrıştırma yapıyoruz.
#

# --- SoloAccounting ---
schema_view_soloaccounting = get_schema_view(
    openapi.Info(
        title="SoloAccounting API",
        default_version="v1",
        description="SoloAccounting ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloaccounting/', include('soloaccounting.api.urls')),
    ],
)

# --- SoloBlog ---
schema_view_soloblog = get_schema_view(
    openapi.Info(
        title="SoloBlog API",
        default_version="v1",
        description="SoloBlog ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloblog/', include('soloblog.api.urls')),
    ],
)

# --- SoloEcommerce ---
schema_view_soloecommerce = get_schema_view(
    openapi.Info(
        title="SoloEcommerce API",
        default_version="v1",
        description="SoloEcommerce ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloecommerce/', include('soloecommerce.api.urls')),
    ],
)

# --- SoloFinance ---
schema_view_solofinance = get_schema_view(
    openapi.Info(
        title="SoloFinance API",
        default_version="v1",
        description="SoloFinance ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/solofinance/', include('solofinance.api.urls')),
    ],
)

# --- SoloInvoice ---
schema_view_soloinvoice = get_schema_view(
    openapi.Info(
        title="SoloInvoice API",
        default_version="v1",
        description="SoloInvoice ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloinvoice/', include('soloinvoice.api.urls')),
    ],
)

# --- SoloPayment ---
schema_view_solopayment = get_schema_view(
    openapi.Info(
        title="SoloPayment API",
        default_version="v1",
        description="SoloPayment ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/solopayment/', include('solopayment.api.urls')),
    ],
)

# --- SoloService ---
schema_view_soloservice = get_schema_view(
    openapi.Info(
        title="SoloService API",
        default_version="v1",
        description="SoloService ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloservice/', include('soloservice.api.urls')),
    ],
)

# --- SoloWeb ---
schema_view_soloweb = get_schema_view(
    openapi.Info(
        title="SoloWeb API",
        default_version="v1",
        description="SoloWeb ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/soloweb/', include('soloweb.api.urls')),
    ],
)

# --- Common ---
schema_view_common = get_schema_view(
    openapi.Info(
        title="Common API",
        default_version="v1",
        description="Common ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/common/', include('common.api.urls')),
    ],
)

# --- SoloSurvey ---
schema_view_solosurvey = get_schema_view(
    openapi.Info(
        title="SoloSurvey API",
        default_version="v1",
        description="SoloSurvey ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/solosurvey/', include('solosurvey.api.urls')),
    ],
)

# --- SoloSite ---
schema_view_solosite = get_schema_view(
    openapi.Info(
        title="SoloSite API",
        default_version="v1",
        description="SoloSite ile ilgili endpoint'ler (Sadece staff).",
    ),
    public=False,
    permission_classes=(OnlyStaffCanSeeDocs,),
    patterns=[
        path('api/solosite/', include('solosite.api.urls')),
    ],
)

#
# 3) URL Patterns
#
urlpatterns = [
    #path('admin/', admin.site.urls),
    path('admin/', solo_admin_site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Tek çatı altında tüm api yönlendirmesi
    path('api/', include('soloadmin.api.urls')),
]

# Debug Toolbar & Static
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

#
# 4) Swagger + ReDoc URL'leri
#    Hem swagger hem redoc ekleyip, sadece staff kullanıcılar görecek şekilde
#
urlpatterns += [
    # SoloAccounting
    path('swagger/soloaccounting/',
         schema_view_soloaccounting.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloaccounting'),
    path('redoc/soloaccounting/',
         schema_view_soloaccounting.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloaccounting'),

    # SoloBlog
    path('swagger/soloblog/',
         schema_view_soloblog.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloblog'),
    path('redoc/soloblog/',
         schema_view_soloblog.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloblog'),

    # SoloEcommerce
    path('swagger/soloecommerce/',
         schema_view_soloecommerce.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloecommerce'),
    path('redoc/soloecommerce/',
         schema_view_soloecommerce.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloecommerce'),

    # SoloFinance
    path('swagger/solofinance/',
         schema_view_solofinance.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-solofinance'),
    path('redoc/solofinance/',
         schema_view_solofinance.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-solofinance'),

    # SoloInvoice
    path('swagger/soloinvoice/',
         schema_view_soloinvoice.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloinvoice'),
    path('redoc/soloinvoice/',
         schema_view_soloinvoice.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloinvoice'),

    # SoloPayment
    path('swagger/solopayment/',
         schema_view_solopayment.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-solopayment'),
    path('redoc/solopayment/',
         schema_view_solopayment.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-solopayment'),

    # SoloService
    path('swagger/soloservice/',
         schema_view_soloservice.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloservice'),
    path('redoc/soloservice/',
         schema_view_soloservice.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloservice'),

    # SoloWeb
    path('swagger/soloweb/',
         schema_view_soloweb.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-soloweb'),
    path('redoc/soloweb/',
         schema_view_soloweb.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-soloweb'),

    # Common
    path('swagger/common/',
         schema_view_common.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-common'),
    path('redoc/common/',
         schema_view_common.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-common'),

    # SoloSurvey
    path('swagger/solosurvey/',
         schema_view_solosurvey.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-solosurvey'),
    path('redoc/solosurvey/',
         schema_view_solosurvey.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-solosurvey'),

    # SoloSite
    path('swagger/solosite/',
         schema_view_solosite.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-solosite'),
    path('redoc/solosite/',
         schema_view_solosite.with_ui('redoc', cache_timeout=0),
         name='schema-redoc-solosite'),
]
