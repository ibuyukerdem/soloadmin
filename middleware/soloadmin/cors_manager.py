"""
Bu middleware, dinamik CORS (Cross-Origin Resource Sharing) kurallarını uygulamak için kullanılır.
Site tablosundan alınan domainler baz alınarak gelen isteklerin `Origin` header'ı kontrol edilir ve
izin verilen domainler için CORS ayarları yanıt başlıklarına eklenir.
"""

from django.contrib.sites.models import Site
from django.http import JsonResponse
from django.core.cache import cache

class DynamicCorsMiddleware:
    """Dinamik CORS ayarlarını uygulayan middleware."""
    def __init__(self, get_response):
        """
        Middleware başlatılırken çağrılır.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Gelen istekler için CORS preflight (OPTIONS) kontrollerini yapar.
        """
        # OPTIONS isteği kontrolü (Preflight)
        if request.method == 'OPTIONS':
            response = JsonResponse({'detail': 'CORS preflight response'}, status=200)
            origin = request.headers.get('Origin', '')  # Origin başlığını al
            if origin in self.get_allowed_domains():  # Eğer origin izinli domainler arasında ise
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
                response["Access-Control-Allow-Credentials"] = "true"
            return response

        # Normal istekler için işlemi bir sonraki aşamaya geçir
        return self.get_response(request)

    def process_response(self, request, response):
        """
        Yanıt başlıklarına CORS ayarlarını ekler.
        """
        origin = request.headers.get('Origin', '')  # Origin başlığını al
        if origin and origin in self.get_allowed_domains():  # Eğer origin izinli domainler arasında ise
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response["Access-Control-Allow-Credentials"] = "true"
        return response

    def get_allowed_domains(self):
        """
        İzin verilen domainleri alır ve cache'de tutar.
        """
        # Cache'te izinli domainleri kontrol et
        allowed_domains = cache.get('allowed_domains')
        if not allowed_domains:
            # Site tablosundan domainleri çek
            domains = Site.objects.values_list('domain', flat=True)
            allowed_domains = set()
            for domain in domains:
                # HTTPS ve HTTP versiyonlarını ekle
                allowed_domains.add(f"https://{domain}")
                allowed_domains.add(f"http://{domain}")
                # www olmayan versiyonları da desteklemek için ekle
                if not domain.startswith("www."):
                    allowed_domains.add(f"https://www.{domain}")
                    allowed_domains.add(f"http://www.{domain}")
            # Cache'e domainleri 1 saat boyunca kaydet
            cache.set('allowed_domains', allowed_domains, timeout=3600)  # 1 saat süre
        return allowed_domains
