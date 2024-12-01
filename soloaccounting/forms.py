"""
Bu kod, Django admin giriş ekranı için özelleştirilmiş bir doğrulama formu tanımlar.
Form, Google reCAPTCHA V3 doğrulamasını kullanarak güvenliği artırır.
"""

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Django admin giriş formunu özelleştirir ve reCAPTCHA doğrulaması ekler.

    Alanlar:
        captcha: Google reCAPTCHA V3 doğrulama alanı.
    """
    captcha = ReCaptchaField(widget=ReCaptchaV3())  # reCAPTCHA V3 alanı ve widget'ı
