from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CustomTokenObtainPairView

schema_view = get_schema_view(
    openapi.Info(
        title="API Dokümantasyonu",
        default_version="v1",
        description="Soloadmin tüm API endpoint'lerinin dokümantasyonu.",
        terms_of_service="https://www.solofor.com/terms/",
        contact=openapi.Contact(email="ibrahim@solofor.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/', include('soloadmin.api.urls')),  # API ana rotası
                  # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

                  # App URL'lerini ekliyoruz
                  # path('finance/', include('solofinance.urls')),
                  # path('service/', include('soloservice.urls')),
                  path('accounting/', include('soloaccounting.urls')),
                  # path('ecommerce/', include('soloecommerce.urls')),
                  # path('web/', include('soloweb.urls')),
                  # path('payment/', include('solopayment.urls')),
                  # path('blog/', include('soloblog.urls')),
                  # path('invoice/', include('soloinvoice.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
