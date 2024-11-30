from django.urls import path, include
from . import views

urlpatterns = [
    path('accounting/', include('soloaccounting.api.urls')),  # soloaccounting API yönlendirmesi
    path('blog/', include('soloblog.api.urls')),  # soloblog API yönlendirmesi
    path('ecommerce/', include('soloecommerce.api.urls')),  # soloecommerce API yönlendirmesi
    path('finance/', include('solofinance.api.urls')),  # solofinance API yönlendirmesi
    path('invoice/', include('soloinvoice.api.urls')),  # soloinvoice API yönlendirmesi
    path('payment/', include('solopayment.api.urls')),  # solopayment API yönlendirmesi
    path('service/', include('soloservice.api.urls')),  # soloservice API yönlendirmesi
    path('web/', include('soloweb.api.urls')),  # soloweb API yönlendirmesi

]
