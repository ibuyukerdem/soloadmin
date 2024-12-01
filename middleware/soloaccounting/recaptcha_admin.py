"""
Bu middleware, admin giriş işlemlerinde Google reCAPTCHA doğrulaması yapar.
Gelen reCAPTCHA yanıtını Google'ın doğrulama API'si ile kontrol eder.
Doğrulama başarısız olursa, erişim engellenir.
"""

import requests
from django.conf import settings
from django.http import HttpResponseForbidden


# soloaccounting/middleware.py

class ReCaptchaAdminMiddleware:
    """Admin giriş işlemleri için reCAPTCHA doğrulaması yapan middleware."""

    def __init__(self, get_response):
        """
        Middleware başlatılırken çağrılır.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Gelen isteklerde reCAPTCHA doğrulaması yapar.
        Sadece admin giriş isteklerinde (`/admin/login/`) çalışır.
        """
        # Admin giriş işlemi kontrolü
        if request.path == '/admin/login/' and request.method == 'POST':
            # reCAPTCHA yanıtını al
            recaptcha_response = request.POST.get('g-recaptcha-response')
            # Doğrulamayı kontrol et
            if not self.verify_recaptcha(recaptcha_response):
                # Doğrulama başarısızsa erişimi engelle
                return HttpResponseForbidden("reCAPTCHA doğrulaması başarısız oldu. Lütfen tekrar deneyin.")

        # Doğrulama başarılıysa işlemi bir sonraki aşamaya geçir
        return self.get_response(request)

    def verify_recaptcha(self, recaptcha_response):
        """
        Google reCAPTCHA doğrulamasını gerçekleştirir ve sonucu döner.
        """
        # Google reCAPTCHA doğrulama verileri
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,  # reCAPTCHA gizli anahtarı
            'response': recaptcha_response  # Kullanıcı tarafından gönderilen reCAPTCHA yanıtı
        }
        try:
            # Google'ın doğrulama API'sine POST isteği gönder
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = response.json()  # Yanıtı JSON formatında al

            # reCAPTCHA v3 için skor ve aksiyon kontrolü
            success = result.get('success', False)  # Doğrulama sonucu
            score = result.get('score', 0)  # Skor (0.0-1.0 arası)
            action = result.get('action', '')  # Kullanıcı aksiyonu (ör. 'login')

            # Başarı durumu, minimum skor ve aksiyonun doğruluğunu kontrol et
            if success and score >= 0.5 and action == 'login':
                return True
            else:
                return False
        except requests.RequestException:
            # API isteği sırasında bir hata oluşursa doğrulama başarısız kabul edilir
            return False
