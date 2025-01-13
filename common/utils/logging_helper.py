from common.models import LogEntry
from common.utils.user_info_extractor import UserInfoExtractor
from django.contrib.sites.models import Site


def log_action(request, model_name, operation, data=None, status='Başarılı', site=None):
    """
    Loglama işlemini gerçekleştirir.
    - site: Manuel olarak gönderilebilir. Gönderilmezse (None), request.user.selectedSite kullanılır.
    - data: Loglamak istediğiniz verileri içeren dict. Eğer içinde dosya nesneleri varsa,
      TemporaryUploadedFile objelerini JSON'a çeviremediğimiz için sadece dosyanın adını vs. tutarız.
    """
    # Kullanıcının IP, browser vb. bilgilerini al
    user_info = UserInfoExtractor.get_user_info(request)

    # Eğer 'site' parametresi None ise request.user.selectedSite değerine başvuruyoruz
    log_site = site or getattr(request.user, 'selectedSite', None)

    # Dosya nesnelerini JSON'a çeviremeyeceğimiz için temizliyoruz:
    cleaned_data = {}
    if isinstance(data, dict):
        for key, value in data.items():
            # TemporaryUploadedFile ya da benzeri bir dosya objesi olabilir
            if hasattr(value, 'read') and hasattr(value, 'name'):
                # Bu bir dosya gibi duruyorsa, sadece adını loglayabiliriz
                cleaned_data[key] = f"FILE: {value.name}"
            else:
                cleaned_data[key] = value
    else:
        # data dict değilse direkt atayabilirsiniz (ama yine de dosya varsa patlayabilir)
        cleaned_data = data

    log_entry = LogEntry.objects.create(
        site=log_site,
        user=user_info['username'],
        ip_address=user_info['ip_address'],
        browser=user_info['browser'],
        operating_system=user_info['operating_system'],
        model_name=model_name,
        operation=operation,
        original_data=cleaned_data,  # Artık JSON serileştirilebilir veri
        status=status,
    )
    print(f"Log oluşturuldu: {log_entry.id}")


def test_log_action():
    """
    Test amaçlı log kaydı oluşturur.
    """
    # Veritabanında mevcut olan bir Site kaydını al
    site, created = Site.objects.get_or_create(
        domain='example.com',
        defaults={'name': 'Example Site'}
    )

    if created:
        print("Yeni site kaydı oluşturuldu.")
    else:
        print("Mevcut site kaydı kullanılıyor.")

    # Sahte bir kullanıcı ve IP bilgisi simüle edelim
    class FakeRequest:
        def __init__(self, site):
            self.META = {
                'REMOTE_ADDR': '192.168.1.1',
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            self.user = type('User', (object,), {'is_authenticated': True, 'username': 'test_user'})()
            self.site = site

    fake_request = FakeRequest(site)
    log_action(fake_request, model_name="TestModel", operation="CREATE", data={"key": "value"}, status="Başarılı")
