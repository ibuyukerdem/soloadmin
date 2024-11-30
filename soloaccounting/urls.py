from django.urls import path

app_name = 'soloaccounting'

urlpatterns = [
    path('', lambda request: None, name='index'),  # Temel bir boş desen
]
