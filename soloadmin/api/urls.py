# soloadmin/api/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('soloaccounting/', include('soloaccounting.api.urls')),  # soloaccounting API yönlendirmesi
    path('soloblog/', include('soloblog.api.urls')),  # soloblog API yönlendirmesi
    path('soloecommerce/', include('soloecommerce.api.urls')),  # soloecommerce API yönlendirmesi
    path('solofinance/', include('solofinance.api.urls')),  # solofinance API yönlendirmesi
    path('soloinvoice/', include('soloinvoice.api.urls')),  # soloinvoice API yönlendirmesi
    path('solopayment/', include('solopayment.api.urls')),  # solopayment API yönlendirmesi
    path('soloservice/', include('soloservice.api.urls')),  # soloservice API yönlendirmesi
    path('soloweb/', include('soloweb.api.urls')),  # soloweb API yönlendirmesi
    path('common/', include('common.api.urls')),  # common API yönlendirmesi
    path('solosurvey/', include('solosurvey.api.urls')),  # common API yönlendirmesi
    path('solosite/', include('solosite.api.urls')),  # common API yönlendirmesi

]
