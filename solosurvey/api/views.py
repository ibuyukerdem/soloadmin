from rest_framework.permissions import IsAuthenticated
from common.base_views import AbstractBaseViewSet
from solosurvey.models import Survey, Question, Choice, SurveyTrigger, SurveyResponse
from .serializers import SurveySerializer, SurveyTriggerSerializer, SurveyResponseSerializer

class SurveyViewSet(AbstractBaseViewSet):
    """
    Site bazlı anket yönetimi ViewSet.
    """
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

class SurveyTriggerViewSet(AbstractBaseViewSet):
    queryset = SurveyTrigger.objects.all()
    serializer_class = SurveyTriggerSerializer
    permission_classes = [IsAuthenticated]

class SurveyResponseViewSet(AbstractBaseViewSet):
    """
    Anket yanıtlarının yönetimi.
    Genelde cevap oluşturma işlemi esnasında gelen 'answers' alanları ile birlikte gelir.
    Burada anonim kullanıcılara izin vermek istenirse ayrıca permission'lar düzenlenebilir.
    """
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Eğer kullanıcı oturum açmışsa respondent olarak set edilebilir.
        # Değilse anonymousIdentifier üzerinden işlem yapılabilir.
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(respondent=user)
