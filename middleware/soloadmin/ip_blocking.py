"""
Bu kod, gelen isteklerin IP adresine göre kara liste kontrolü ve hız sınırlandırma işlemlerini gerçekleştirir.
Eğer bir IP kara listedeyse veya belirlenen hız sınırını aşarsa, isteğe erişim engellenir.
"""

from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
from django.core.cache import cache
from django.urls import resolve
from soloaccounting.models import Blacklist

# Maksimum izin verilen istek sayısı (örneğin, dakikada 100 istek)
RATE_LIMIT = 100

def get_client_ip(request):
    """
    İsteği yapan istemcinin IP adresini döner.
    X-Forwarded-For başlığı varsa kullanılır, aksi halde REMOTE_ADDR döner.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def update_request_log(client_ip):
    """
    İlgili IP adresine ait istek zamanlarını günceller ve son bir dakikadaki toplam istek sayısını döner.
    """
    now = datetime.now()
    key = f"requests_{client_ip}"  # IP adresine özel cache anahtarı
    request_times = cache.get(key, [])
    # Son bir dakika içinde yapılan istekleri filtrele
    request_times = [req for req in request_times if now - req <= timedelta(minutes=1)]
    request_times.append(now)  # Yeni isteği zaman kaydına ekle
    cache.set(key, request_times, timeout=60)  # Güncellenen listeyi cache'e kaydet
    return len(request_times)

def blacklist_ip(ip_address, reason="Aşırı istek"):
    """
    Belirtilen IP adresini kara listeye ekler ve kara liste kaydını veritabanında saklar.
    """
    key = f"blacklisted_{ip_address}"  # IP adresine özel cache anahtarı
    if not cache.get(key):  # IP zaten kara listedeyse işlem yapılmaz
        cache.set(key, True, timeout=3600)  # IP'yi 1 saat boyunca kara listede tut
        # Kara liste veritabanına kaydet
        Blacklist.objects.create(ip_address=ip_address, reason=reason, is_active=True)

class BlockIPMiddleware:
    """
    Kara liste kontrolü ve hız sınırlandırma yapan middleware.
    """
    def __init__(self, get_response):
        """
        Middleware başlatılırken çağrılır.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Her istek için çağrılır. Kara liste kontrolü ve hız sınırlandırmayı uygular.
        """
        # Admin uygulamasına yapılan istekler kontrol dışı bırakılır
        if resolve(request.path).app_name == 'admin':
            return self.get_response(request)

        # İstemcinin IP adresini al
        client_ip = get_client_ip(request)

        # Kara listedeki IP adreslerini kontrol et
        blacklisted_ips = Blacklist.objects.filter(is_active=True).values_list('ip_address', flat=True)
        if client_ip in blacklisted_ips:
            # Kara listedeki IP'ler için erişimi engelle
            return HttpResponseForbidden("Erişiminiz kara listeye alınmıştır.")

        # İstek logunu güncelle ve istek sayısını al
        request_count = update_request_log(client_ip)
        if request_count > RATE_LIMIT:
            # Hız sınırını aşan IP'yi kara listeye ekle
            blacklist_ip(client_ip)
            return HttpResponseForbidden("Aşırı istek nedeniyle IP'niz kara listeye alınmıştır.")

        # Kontrolleri geçen isteği bir sonraki aşamaya gönder
        return self.get_response(request)
