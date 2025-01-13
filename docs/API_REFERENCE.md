# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.


# DRF-YASG Kullanımı ve Erişimi

**Kurulum:**
```bash
pip install drf-yasg
settings.py:

python
Kodu kopyala
INSTALLED_APPS += ['drf_yasg']
urls.py:

python
Kodu kopyala
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Dokümantasyonu",
        default_version="v1",
        description="Proje API açıklamaları",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
Erişim:

Swagger UI: http://127.0.0.1:8000/swagger/
ReDoc: http://127.0.0.1:8000/redoc/

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.

---

# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.