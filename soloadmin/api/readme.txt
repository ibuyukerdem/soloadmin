Django Projesi API Yapısı ve Sub-App Yönetimi
1. Amaç
Bu doküman, Django projelerinde API yönetimi için merkezi bir yapı oluşturmayı, tüm ana app ve sub-app URL'lerinin proje genelinde bir merkezi API rotası altında toplanmasını ve bu yapıların kolayca genişletilmesini açıklar.

2. Doğru Dizin Yapısı
Aşağıdaki yapı, büyük ve karmaşık projeler için önerilen API dizin düzenini temsil eder. Sub-app'ler, ana app'lere bağlı şekilde entegre edilir ve tüm API URL'leri proje genelinde merkezi bir yerde (soloadmin/api/urls.py) toplanır.

project_root/
├── manage.py
├── db.sqlite3
├── soloadmin/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py            # Proje genelinde tüm URL rotalarını barındırır
│   ├── asgi.py
│   ├── wsgi.py
│   ├── api/               # Merkezi API yönetimi
│   │   ├── __init__.py
│   │   ├── urls.py        # Tüm ana app ve sub-app API rotalarının yönlendirildiği dosya
│   │   ├── views.py       # Ortak API endpoint'leri (örneğin sağlık kontrolü)
│   │   └── serializers.py # Ortak API serializer'ları
├── soloaccounting/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── api/               # Ana app için API
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── reports/           # Sub-app dizini
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── api/           # Sub-app için API
│   │   │   ├── __init__.py
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   ├── admin.py
│   │   └── tests.py
├── soloblog/
│   ├── ...
└── soloecommerce/
    ├── ...
3. Sub-App URL Yönetimi
Proje Ana urls.py:
soloadmin/urls.py, tüm ana app ve sub-app URL'lerini proje genelinde yönlendirmek için merkezi bir yerdir.

Örnek: soloadmin/urls.py

from django.urls import path, include

urlpatterns = [
    path('api/', include('soloadmin.api.urls')),  # Merkezi API yönetimi
]

Merkezi API Yönlendirme:
soloadmin/api/urls.py tüm ana app ve sub-app API rotalarını barındırır.

Örnek: soloadmin/api/urls.py

from django.urls import path, include

urlpatterns = [
    path('accounting/', include('soloaccounting.api.urls')),  # Ana app API rotası
    path('accounting/reports/', include('soloaccounting.reports.api.urls')),  # Sub-app API rotası
    path('blog/', include('soloblog.api.urls')),  # Diğer ana app
]

Ana App urls.py:
Ana app kendi API rotalarını içerir.

Örnek: soloaccounting/api/urls.py

python
Kodu kopyala
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountingAPIView.as_view(), name='accounting_api'),
]
Sub-App urls.py:
Sub-app kendi API rotalarını içerir.

Örnek: soloaccounting/reports/api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportAPIView.as_view(), name='report_api'),
]

4. Ortak API Endpoint'leri
Merkezi soloadmin/api/views.py dosyasında proje genelinde kullanılabilecek ortak endpoint'ler oluşturabilirsiniz.

Örnek: Sağlık Kontrolü Endpoint'i

from rest_framework.views import APIView
from rest_framework.response import Response

class HealthCheckAPIView(APIView):
    """
    API Sağlık Durumu Kontrolü
    """
    def get(self, request):
        return Response({'status': 'OK', 'message': 'API çalışıyor!'})
Bu endpoint'i soloadmin/api/urls.py dosyasına ekleyin:


from django.urls import path, include
from .views import HealthCheckAPIView

urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health_check'),  # Sağlık kontrolü
    path('accounting/', include('soloaccounting.api.urls')),
    path('accounting/reports/', include('soloaccounting.reports.api.urls')),
]

5. Otomatik API Dizin Oluşturma Aracı
Bu araç, her app ve sub-app için api dizinini otomatik oluşturur.

Kod: create_api_structure.py

import os
import sys

def create_api_structure_for_app(app_name, base_path=os.getcwd()):
    """
    Verilen app veya sub-app için API dizin yapısını oluşturur.

    Args:
        app_name (str): API yapısının oluşturulacağı app veya sub-app adı.
                        Örneğin: "soloaccounting" veya "soloaccounting/reports".
    """
    app_api_path = os.path.join(base_path, app_name, "api")
    os.makedirs(app_api_path, exist_ok=True)

    api_files = ["__init__.py", "urls.py", "views.py", "serializers.py"]
    for file_name in api_files:
        file_path = os.path.join(app_api_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                if file_name == "urls.py":
                    file.write(
                        "from django.urls import path\n"
                        "from . import views\n\n"
                        "urlpatterns = [\n"
                        "    path('', views.ExampleAPIView.as_view(), name='example_api'),\n"
                        "]\n"
                    )
                elif file_name == "views.py":
                    file.write(
                        "from rest_framework.views import APIView\n"
                        "from rest_framework.response import Response\n\n"
                        "class ExampleAPIView(APIView):\n"
                        "    def get(self, request):\n"
                        "        return Response({'message': 'Bu bir örnek API yanıtıdır.'})\n"
                    )

    print(f"API yapısı '{app_name}' için başarıyla oluşturuldu.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
        create_api_structure_for_app(app_name)
    else:
        print("Lütfen bir app adı belirtin. Örnek: python create_api_structure.py soloaccounting")

6. Avantajlar
Merkezi API Yönetimi: Tüm ana app ve sub-app URL'leri merkezi bir yerde toplanır.
Kolay Genişletilebilirlik: Yeni bir app veya sub-app eklemek hızlıdır.
Modülerlik: Ana app ve sub-app API'leri bağımsız çalışabilir.
Bu yapı, büyük ve karmaşık projelerde düzenli ve genişletilebilir bir API yönetimi sağlar.