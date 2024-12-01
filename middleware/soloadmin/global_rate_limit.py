"""
Bu middleware, gelen istekler için genel bir hız sınırlandırması (rate limit) uygular.
İstekler belirli bir oranı aşarsa (örneğin dakikada 25 istek), yanıt olarak HTTP 429 (Too Many Requests) döndürür.
"""

from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import is_ratelimited
from django.http import JsonResponse


class GlobalRateLimitMiddleware:
    """Genel hız sınırlandırması (rate limit) uygulayan middleware."""

    def __init__(self, get_response):
        """
        Middleware başlatılırken çağrılır.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Her istek için çağrılır ve hız sınırlandırması kontrolü yapar.
        """
        try:
            # İsteklerin IP adresine göre dakikada 25 istekle sınırlanması
            if is_ratelimited(
                    request,
                    group='global',  # Rate limit grubunun adı
                    key='ip',  # IP adresine göre sınırlandır
                    rate='25/m',  # Dakikada 25 istek sınırı
                    method=['GET', 'POST']  # Yalnızca GET ve POST istekleri için geçerli
            ):
                # Limit aşımı durumunda özel hata yanıtı döndür
                return JsonResponse(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=429  # HTTP 429: Too Many Requests
                )
        except Ratelimited:
            # Rate limit durumu yakalandığında hata yanıtı döndür
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )

        # Sınırı aşmayan isteği bir sonraki aşamaya geçir
        return self.get_response(request)
