from django.urls import path

app_name = 'soloecommerce'
urlpatterns = [
    path('', lambda request: None, name='index'),  # Temel bir boş desen
]
