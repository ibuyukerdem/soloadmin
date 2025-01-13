from rest_framework.views import APIView
from rest_framework.response import Response

class ExampleAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Bu bir örnek API yanıtıdır.'})
