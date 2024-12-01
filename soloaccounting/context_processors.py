"""
Bu fonksiyon, Django'daki `context processor` olarak kullanılabilir.
Şablonlara (templates) Google reCAPTCHA'nın `public key` (site anahtarı) bilgisini ekler.
Bu sayede şablonlar üzerinden reCAPTCHA entegrasyonu kolaylıkla yapılabilir.
"""

from django.conf import settings


def recaptcha_key(request):
    """
    Şablonlara `RECAPTCHA_PUBLIC_KEY` değişkenini ekler.

    Returns:
        dict: Şablonlara gönderilecek `RECAPTCHA_PUBLIC_KEY` değerini içeren sözlük.
    """
    return {
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY,  # Google reCAPTCHA site anahtarı
    }
