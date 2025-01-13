from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, SurveyTriggerViewSet, SurveyResponseViewSet

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='surveys')
router.register(r'triggers', SurveyTriggerViewSet, basename='triggers')
router.register(r'responses', SurveyResponseViewSet, basename='responses')

urlpatterns = [
    path('', include(router.urls)),
]
