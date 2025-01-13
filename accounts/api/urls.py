from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExampleAPIView.as_view(), name='example_api'),
]
