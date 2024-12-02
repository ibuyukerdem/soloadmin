from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from soloaccounting.models import CustomUser
from .serializers import UserSummarySerializer, UserDetailSerializer, CustomUserSerializer


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'username', 'email', 'isIndividual']  # Filtrelemek istediğiniz alanlar
    search_fields = ['username', 'email']  # Arama için kullanılacak alanlar
    ordering_fields = ['id', 'username', 'email']  # Sıralama için kullanılacak alanlar
    ordering = ['id']  # Varsayılan sıralama

    def get_serializer_class(self):
        """
        Özet veya detay serializer'ı seçmek için `action`'a bağlı bir yapı.
        """
        if self.action == 'list':
            return UserSummarySerializer
        return UserDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user  # Giriş yapan kullanıcı
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)
