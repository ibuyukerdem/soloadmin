from django.urls import path

app_name = 'soloservice'

urlpatterns = [
    path('', lambda request: None, name='index'),  # Temel bir boş desen
]