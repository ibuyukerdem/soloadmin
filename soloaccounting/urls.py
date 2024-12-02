from django.urls import path, include

urlpatterns = [
    # Diğer uygulama yollarını buraya ekleyebilirsiniz
    path('api/', include('soloaccounting.api.urls')),
]
