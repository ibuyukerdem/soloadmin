"""
Bu middleware, gelen isteklerin body boyutunu ve gerekli header içeriklerini kontrol eder.
Eğer kontrol başarısız olursa, isteğe izin verilmez ve bir hata yanıtı döndürülür.
"""

from django.http import JsonResponse
from django.urls import resolve

class ValidateRequestMiddleware:
    """Gelen isteğin body ve header içeriklerini kontrol eden middleware."""
    def __init__(self, get_response):
        """
        Middleware başlatılırken çağrılır.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Her istek için çağrılır ve aşağıdaki kontroller uygulanır:
        - Admin paneli isteklerini hariç tutar.
        - İstek boyutunu kontrol eder.
        - Zorunlu header içeriklerini kontrol eder.
        """
        # Admin paneli isteklerini hariç tut
        if resolve(request.path).app_name == 'admin':
            return self.get_response(request)

        # Belirli endpoint'leri hariç tut
        EXCLUDED_PATHS = ['/api/token/', '/api/token/refresh/']
        if request.path in EXCLUDED_PATHS:
            return self.get_response(request)

        # İstek Boyutunu Kontrol Et
        MAX_BODY_SIZE = 1024 * 1024  # Maksimum body boyutu: 1 MB
        if request.method in ['POST', 'PUT', 'PATCH'] and len(request.body) > MAX_BODY_SIZE:
            # Eğer body boyutu 1 MB'ı aşarsa hata döndür
            return JsonResponse(
                {"error": "İstek boyutu 1 MB'ı geçemez."},
                status=413  # HTTP 413: Payload Too Large
            )

        # Zorunlu Header Kontrolü
        REQUIRED_HEADERS = ['X-Requested-With', 'Authorization']  # İstenen header listesi
        missing_headers = [header for header in REQUIRED_HEADERS if header not in request.headers]
        if missing_headers:
            # Eksik header varsa hata döndür
            return JsonResponse(
                {"error": f"Zorunlu başlıklar eksik: {', '.join(missing_headers)}"},
                status=400  # HTTP 400: Bad Request
            )

        # Tüm kontrollerden geçen isteği bir sonraki aşamaya gönder
        return self.get_response(request)
