from django.urls import path

app_name = 'soloblog'

urlpatterns = [
    path('', lambda request: None, name='index'),  # Temel bir boş desen
]
