from django.urls import path
from .views import UserSummaryView, UserDetailView

urlpatterns = [
    path('user/summary/', UserSummaryView.as_view(), name='user-summary'),
    path('user/detail/', UserDetailView.as_view(), name='user-detail'),
]
