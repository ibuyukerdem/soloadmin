# common/exceptions.py

from rest_framework.views import exception_handler
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
    NotFound,
)

def custom_exception_handler(exc, context):
    """
    Proje genelindeki tüm API istisnalarını tek noktada yakala
    ve ortak bir JSON formatıyla döndür.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # DRF’in oluşturduğu varsayılan hata içeriği (detail) varsa al.
        default_detail = response.data.get('detail', '')

        # Hata türüne göre i18n destekli mesaj örneği:
        if isinstance(exc, NotAuthenticated):
            message = _("Lütfen giriş yapın.")  # "Please log in."
            code = "not_authenticated"
        elif isinstance(exc, PermissionDenied):
            message = _("Bu işlem için yeterli izniniz yok.")  # "You do not have permission."
            code = "permission_denied"
        elif isinstance(exc, NotFound):
            message = _("Aradığınız kaynak bulunamadı.")  # "Not found."
            code = "not_found"
        elif isinstance(exc, ValidationError):
            # ValidationError genelde dict/list dönebilir;
            # bunu olduğu gibi "errors" içine atabilirsiniz.
            code = "validation_error"
            # Örneğin, `response.data` içinde {"fieldName": ["Bu alan zorunludur."]} gibi
            # bir yapı varsa bunu doğrudan errors'a koyabilirsiniz.
            message = _("Gönderilen verilerde doğrulama hatası var.")
        else:
            message = default_detail or str(exc)
            code = "error"

        # Orijinal `response.data`'yı temizleyip kendi formatınızı kurun:
        # Örneğin:
        # {
        #   "success": false,
        #   "code": "permission_denied",
        #   "message": "Bu işlem için yeterli izniniz yok.",
        #   "errors": { "fieldName": ["Mesaj..."] }  # ValidationError varsa
        # }
        original_data = dict(response.data)  # orijinal veriyi saklayın
        response.data.clear()

        response.data["success"] = False
        response.data["code"] = code
        response.data["message"] = message

        # Eğer ValidationError ise, alan bazlı hataları "errors" içine koyun:
        if isinstance(exc, ValidationError):
            response.data["errors"] = original_data
        else:
            response.data["errors"] = {}

    return response
