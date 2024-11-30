import os
import sys

def create_api_structure_for_app(app_name, base_path=os.getcwd()):
    """
    Verilen app veya sub-app için API dizin yapısını oluşturur.

    Args:
        app_name (str): API yapısının oluşturulacağı app veya sub-app adı.
                        Örneğin: "soloaccounting" veya "soloaccounting/reports".
        base_path (str): Proje ana dizini (varsayılan olarak mevcut çalışma dizini).

    Bu fonksiyon, verilen app için aşağıdaki yapıyı oluşturur:
        app_name/
        └── api/
            ├── __init__.py
            ├── urls.py
            ├── views.py
            └── serializers.py

    Kullanım:
        - Ana bir app için: python create_api_structure.py soloaccounting
        - Sub-app için: python create_api_structure.py soloaccounting/reports
    """
    # App dizin yolu
    app_api_path = os.path.join(base_path, app_name, "api")
    os.makedirs(app_api_path, exist_ok=True)

    # API altındaki dosyalar
    api_files = ["__init__.py", "urls.py", "views.py", "serializers.py"]
    for file_name in api_files:
        file_path = os.path.join(app_api_path, file_name)
        if not os.path.exists(file_path):  # Eğer dosya zaten mevcut değilse oluştur
            with open(file_path, "w", encoding="utf-8") as file:
                # urls.py içeriği
                if file_name == "urls.py":
                    file.write(
                        "from django.urls import path\n"
                        "from . import views\n\n"
                        "urlpatterns = [\n"
                        "    path('', views.ExampleAPIView.as_view(), name='example_api'),\n"
                        "]\n"
                    )
                # views.py içeriği
                elif file_name == "views.py":
                    file.write(
                        "from rest_framework.views import APIView\n"
                        "from rest_framework.response import Response\n\n"
                        "class ExampleAPIView(APIView):\n"
                        "    def get(self, request):\n"
                        "        return Response({'message': 'Bu bir örnek API yanıtıdır.'})\n"
                    )
                # serializers.py içeriği
                elif file_name == "serializers.py":
                    file.write(
                        "from rest_framework import serializers\n\n"
                        "class ExampleSerializer(serializers.Serializer):\n"
                        "    example_field = serializers.CharField()\n"
                    )

    print(f"API yapısı '{app_name}' app'i için başarıyla oluşturuldu.")

if __name__ == "__main__":
    """
    Komut satırından app adını alarak API yapısı oluşturur.
    Örnek:
        - python create_api_structure.py soloaccounting
        - python create_api_structure.py soloaccounting/reports
    """
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
        create_api_structure_for_app(app_name)
    else:
        print("Lütfen bir app adı belirtin. Örnek: python create_api_structure.py soloaccounting")
