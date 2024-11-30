from django.urls import path

app_name = 'soloinvoice'

urlpatterns = [
    path('', lambda request: None, name='index'),  # Ana sayfa için boş bir desen
]
