from django.urls import path

app_name = 'soloweb'

urlpatterns = [
    # Örnek bir boş URL deseni
    path('', lambda request: None, name='index'),
]
