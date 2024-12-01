"""
Bu middleware, gelen HTTP isteğinin host adını kullanarak Django'nun Site modelinden ilgili site nesnesini belirler.
Eğer bir eşleşme bulunursa, isteğe (request) `site` ve varsa ilişkili `module` bilgilerini ekler.
Bu sayede, farklı sitelere özel işlem yapma imkanı sağlar.
"""
from django.contrib.sites.models import Site

class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # Django'nun isteği işleme bağlantı noktası

    def __call__(self, request):
        # Host adını al ve port bilgisi varsa çıkar
        host = request.get_host().split(':')[0]
        try:
            # Host adına uygun Site nesnesini al
            site = Site.objects.get(domain=host)
            request.site = site  # İstek nesnesine Site bilgisi ekle
            # İlgili modül bilgisi varsa isteğe ekle
            request.module = site.module.module if hasattr(site, 'module') else None
        except Site.DoesNotExist:
            # Site bulunamazsa isteğe None ekle
            request.site = None
            request.module = None
        # İsteği bir sonraki aşamaya gönder
        return self.get_response(request)
