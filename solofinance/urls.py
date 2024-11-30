from django.urls import path

app_name = 'solofinance'
urlpatterns = [
    path('', lambda request: None, name='index'),  # Temel bir boş desen
]
