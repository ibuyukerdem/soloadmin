from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from soloaccounting.admin import custom_admin_site

schema_view = get_schema_view(
    openapi.Info(
        title="API Dokümantasyonu",
        default_version="v1",
        description="Projenin tüm API endpoint'lerinin dokümantasyonu.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    #path('admin/', custom_admin_site.urls),
    # path('captcha/', include('captcha.urls')),
    path('admin/', admin.site.urls),

    path('api/', include('soloadmin.api.urls')),  # API ana rotası
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # App URL'lerini ekliyoruz
    # path('finance/', include('solofinance.urls')),
    # path('service/', include('soloservice.urls')),
    # path('accounting/', include('soloaccounting.urls')),
    # path('ecommerce/', include('soloecommerce.urls')),
    # path('web/', include('soloweb.urls')),
    # path('payment/', include('solopayment.urls')),
    # path('blog/', include('soloblog.urls')),
    # path('invoice/', include('soloinvoice.urls')),
]
