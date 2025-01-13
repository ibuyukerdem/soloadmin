# middleware/soloadmin/UserTimezone.py
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.utils import translation

class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response



    def __call__(self, request):
        # Kullanıcı giriş yapmış ve timezone seçmiş ise onu kullan
        if request.user.is_authenticated and getattr(request.user, 'timezone', None):
            try:
                user_tz = ZoneInfo(request.user.timezone)
                timezone.activate(user_tz)
                translation.activate(request.user.preferred_language)
            except Exception:
                # Geçersiz bir timezone varsa varsayılan ata
                timezone.activate(ZoneInfo("Europe/Istanbul"))
        else:
            # Kullanıcı giriş yapmamışsa varsayılan timezone'u kullan
            timezone.activate(ZoneInfo("Europe/Istanbul"))
            translation.activate('en')

        response = self.get_response(request)
        return response
