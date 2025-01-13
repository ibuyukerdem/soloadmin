from django.urls import path, include
from .views import trigger_error

urlpatterns = [
    # Diğer uygulama yollarını buraya ekleyebilirsiniz
    path('api/', include('soloaccounting.api.urls')),
    path('test-error/', trigger_error),
]
