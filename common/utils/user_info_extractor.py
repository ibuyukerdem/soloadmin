class UserInfoExtractor:
    """
    Kullanıcı bilgilerini HTTP isteklerinden çıkaran yardımcı sınıf.
    """

    @staticmethod
    def get_user_info(request):
        """
        Kullanıcı bilgilerini çıkarır.
        """
        user_agent = request.META.get('HTTP_USER_AGENT', 'Bilinmeyen Tarayıcı')
        ip_address = request.META.get('REMOTE_ADDR', 'Bilinmeyen IP')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]

        return {
            "user_agent": user_agent,
            "ip_address": ip_address,
            "username": request.user.username if request.user.is_authenticated else "Anonim",
            "browser": UserInfoExtractor.get_browser_info(user_agent),
            "operating_system": UserInfoExtractor.get_os_info(user_agent),
        }

    @staticmethod
    def get_browser_info(user_agent):
        """
        Tarayıcı bilgilerini analiz eder.
        """
        if 'Chrome' in user_agent:
            return "Google Chrome"
        elif 'Firefox' in user_agent:
            return "Mozilla Firefox"
        elif 'Safari' in user_agent:
            return "Apple Safari"
        elif 'Edge' in user_agent:
            return "Microsoft Edge"
        elif 'MSIE' in user_agent or 'Trident' in user_agent:
            return "Internet Explorer"
        return "Bilinmeyen Tarayıcı"

    @staticmethod
    def get_os_info(user_agent):
        """
        İşletim sistemi bilgilerini analiz eder.
        """
        if 'Windows' in user_agent:
            return "Windows"
        elif 'Macintosh' in user_agent or 'Mac OS X' in user_agent:
            return "Mac OS"
        elif 'Linux' in user_agent:
            return "Linux"
        elif 'Android' in user_agent:
            return "Android"
        elif 'iPhone' in user_agent or 'iPad' in user_agent:
            return "iOS"
        return "Bilinmeyen İşletim Sistemi"
