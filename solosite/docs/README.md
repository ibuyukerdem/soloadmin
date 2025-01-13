# **5. Rol Kontrolü (Basit Örnek)**

<https://chatgpt.com/c/6765ce32-984c-8006-b820-7e401d7ce231>

# Uygulama içi bir işlem yapmadan önce kullanıcının ilgili role sahip olup olmadığını kontrol etmek isteyebilirsiniz.

```
def has_solosite_role(user, role_code):
    """
    user -> Django CustomUser (AUTH_USER_MODEL)
    role_code -> Ör: "admin", "manager", vs.
    """
    if not user.is_authenticated:
        return False

    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        return False

    # Kullanıcının solositeRoles'lerine bak
    assigned_roles = user_profile.solositeRoles.select_related('role').all()
    # user_profile.solositeRoles => SiteUserRole queryset

    for user_role in assigned_roles:
        if user_role.role.code == role_code:
            return True

    return False
```

# Ardından bir **View** veya **Service** katmanında:

```
# Örnek Django Rest Framework bazlı view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from solosite.utils import has_solosite_role

class SomeProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_solosite_role(request.user, "admin"):
            return Response({"detail": "Sadece Admin rolü erişebilir."}, status=403)
        return Response({"message": "İçerik..."})
```

### **6. UserProfile’ı Genişletme (Proje Gereksinimine Göre)**

### **6.1. accounts/models.py Örneği (Daha Geniş)**

```
# accounts/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    bio = models.TextField(blank=True, null=True)
    # Örneğin global roller için M2M ya da diğer alanlar eklenebilir
    # E-posta onay durumu, KVKK onay bilgisi gibi ekstra alanlar da buraya eklenebilir

    def __str__(self):
        return f"{self.user.username} – Profile
   @property
    def full_name(self):
        # Örnek bir property
        return f"{self.user.first_name} {self.user.last_name}"
```

### **7. Adım Adım Özet**

### **common.CustomUser:**

### AUTH_USER_MODEL olarak ayarlanır.

### Temel kullanıcı verisi ve kimlik doğrulama (username, email, password vb.) burada.

### **accounts.UserProfile:**

### OneToOneField ile CustomUser’a bağlı.

### Proje genelinde kullanıcıya eklenmesi gereken alanlar burada toplanır.

### Uygulama bazlı roller bu profile bağlanır.

### **Uygulama Bazlı Rol Tanımları (Örn. solosite.models):**

### SiteRole (admin, manager, staff gibi roller)

### SiteUserRole (hangi UserProfile hangi SiteRole’a sahip)

### (İsteğe bağlı) SitePermission ve SiteRolePermission ile detaylı izin yönetimi

### **Atama ve Kontrol:**

### UserProfile nesnesine rol atamak için SiteUserRole.objects.create(...)

### Kontrol için yardımcı fonksiyonlar (örneğin has_solosite_role, has_permission)

### View katmanında izin kontrolleri

### **UserProfile Genişletme:**

### Proje ilerledikçe kullanıcıyla ilgili ek alan veya fonksiyonellik gerektiğinde, accounts.models.UserProfile modeline alanlar eklenebilir.

### 

### **Sonuç**

### Bu rehberde:

### common uygulamasında yer alan **CustomUser** modeli projenin kimlik doğrulama temeli olarak kullanılır.

### accounts uygulamasındaki **UserProfile** modeli, kullanıcıya ait ek demografik/verisel bilgileri ve rollerin merkezini oluşturur.

### Her uygulama (solosite, soloaccounting vb.) kendi **rol** ve **izin** modellerini tanımlayarak kullanıcı profiliyle ilişkilendirir.

### Bu yaklaşım sayesinde model dosyaları şişmeden, her uygulamanın kendine özgü rol mantığını koruyabileceği, ancak yine de tek bir kullanıcı/profil kaynağından yönetilen tutarlı bir sistem ortaya çıkar.

### Bu mimariyi izleyerek projeyi büyütmeniz, yeni uygulamalar eklemeniz veya mevcut uygulamalardaki rol ve izinleri geliştirmeniz oldukça kolay ve sürdürülebilir hale gelecektir.

### 

# Proje Genel Bakış ve Yol Haritası

## Projenin Amacı

Bu proje, bir veya birden fazla sitenin (konut, iş merkezi vb.) yönetim faaliyetlerini tek bir platform üzerinden etkin ve verimli şekilde yürütmeyi amaçlar. Hem Türkiye hem de Avrupa mevzuatına uyumlu, çok dilli, çoklu para birimi destekli, ölçeklenebilir bir yapı kurulacaktır.

**Hedeflenen Özellikler ve Kapsam:**

-   **Gelir-Gider Yönetimi:** Aidat, kira, bakım, onarım, spor salonu ücretleri, otopark kullanım ücretleri gibi tüm mali işlemleri takip etmek.
-   **Personel ve İK Yönetimi:** Personel maaşları, izinler, mesai, huzur hakları, özlük dosyaları, performans takibi.
-   **Varlık ve Ortak Alan Yönetimi:** Otopark alanları, spor salonu üyelikleri, toplantı odası rezervasyonları, bakım-onarım takibi.
-   **Kiracı Yönetimi:** Kira sözleşmesi, ödeme hatırlatmaları, kira artışı, depozito takipleri.
-   **Veri Güvenliği ve Yasal Uyum:** KVKK, GDPR, E-Fatura, IFRS/MUHASEBE standartları, e-imza entegrasyonları.
-   **Uluslararası Desteği:** Çok dilli arayüz, çoklu para birimi (TRY, EUR vb.), yerel mevzuata uyum.
-   **Raporlama ve Denetim:** Finansal raporlar, personel raporları, audit log, bakım geçmişi.

## Teknolojik Altyapı

-   **Arka Uç (Backend):**
    -   **Django & Django Rest Framework (DRF):** API tabanlı mimari, JWT/Session bazlı yetkilendirme.
    -   **Veritabanı:** PostgreSQL veya MySQL (tercihen PostgreSQL)
    -   **Kimlik ve Erişim Yönetimi:** Django’nun yerleşik kullanıcı modeli + gruplar & izinler.
-   **Ön Yüz (Frontend) (İleri Aşamada):**
    -   **Next.js:** SSR/SSG desteği, i18n desteği
    -   **UI Kütüphanesi:** TailwindCSS, Chakra UI vb. seçenekler değerlendirilebilir.
-   **Entegrasyonlar:**
    -   E-Fatura API’leri (Türkiye)
    -   Online ödeme servisleri (Iyzico, Stripe vb.)
    -   Dijital imza / e-imza sağlayıcıları
    -   OCR plaka tanıma sistemleri (otopark modu için)

## Modüller ve Özellikleri

Aşağıda modüller aşama aşama, öncelikli temel özelliklerden daha gelişmiş özelliklere doğru sıralanmıştır. Bu yaklaşım MVP (Minimum Viable Product) odaklı geliştirmeye olanak sağlar.

### Aşama 1: Temel Yapı ve Çekirdek Özellikler

1.  **Kullanıcı Yönetimi (Temel)**
    -   Kullanıcı oluşturma, giriş/çıkış işlemleri
    -   Rol tabanlı yetki yapısı (Yönetici, Personel, Muhasebe, Sakin)
    -   Django Admin arayüzünde başlangıç konfigürasyonları
2.  **Site ve Blok Yönetimi (Temel)**
    -   Birden fazla site tanımlama (Django Site modeli ile ilişki)
    -   Blok/Daire tanımları, adres bilgileri
3.  **Aidat ve Gelir-Gider Yönetimi (Temel)**
    -   Aidat tanımlamaları
    -   Gelir-gider kayıtlarının manuel eklenmesi
    -   Basit raporlama (Toplam gelir, toplam gider)
4.  **Kiracı Yönetimi (Temel)**
    -   Kiracı bilgileri (temel iletişim, kimlik bilgileri)
    -   Kira kontrat başlangıç/bitiş tarihi, aylık tutar kaydı
    -   Kira ödemelerinin manuel işlenmesi
5.  **Personel Yönetimi (Temel)**
    -   Personel bilgileri (iletişim, SGK no, pozisyon)
    -   Maaş ödemelerinin manuel kaydı

### Aşama 2: Genişletilmiş Özellikler

1.  **Gelir-Gider Yönetimi (Gelişmiş)**
    -   Otomatik ödeme hatırlatma e-postaları
    -   Online ödeme entegrasyonları (Iyzico, Stripe)
    -   IFRS ve yerel muhasebe formatlarına uygun raporlar
2.  **Otopark Yönetimi (Temel)**
    -   Otopark alanı tanımları (numaralandırma, kat)
    -   Araç kaydı (plaka, marka/model)
    -   Otopark izinleri (daireye atanan veya kiralanan alanlar)
3.  **Spor Salonu Üyelik Sistemi (Temel)**
    -   Üyelik tipleri (aylık, yıllık)
    -   Üyelik başlangıç/bitiş tarihleri
    -   Basit giriş takibi
4.  **Bakım ve Onarım Talep Yönetimi (Temel)**
    -   Site sakinleri tarafından oluşturulan bakım talepleri
    -   Bakım personeline atama
    -   Talebin durum güncellemeleri (Bekliyor, Tamamlandı vb.)
5.  **Çoklu Dil ve Para Birimi Desteği (Temel)**
    -   Django i18n alt yapısının aktifleştirilmesi
    -   UI metinleri için çoklu dil dosyaları
    -   Kur bilgisi: Merkez Bankası API’si ile anlık kur takibi

### Aşama 3: İleri Özellikler

1.  **Kiracı Yönetimi (Gelişmiş)**
    -   Kira artış hesaplamaları (TÜFE, yasal limitler)
    -   Otomatik kira ödeme hatırlatmaları (E-posta, SMS)
    -   Gecikme faizi hesaplama
2.  **Personel Yönetimi (Gelişmiş)**
    -   İzin yönetimi (yıllık izin, hastalık izni)
    -   Vardiya planlama
    -   Performans değerlendirme kayıtları
    -   Maaş bordrosu oluşturma ve arşivleme
3.  **Spor Salonu Üyelik Sistemi (Gelişmiş)**
    -   Rezervasyon sistemi (ders, eğitmen, ekipman rezervasyonu)
    -   Giriş-çıkış istatistikleri ve raporlar
    -   QR kod/RFID ile giriş kontrolleri
4.  **Otopark Yönetimi (Gelişmiş)**
    -   Plaka tanıma sistemi entegrasyonu (OCR)
    -   Misafir araç izinleri
    -   Otopark doluluk raporları
    -   Ücretli otopark modelleri (saatlik, abonelik)
5.  **Bakım-Onarım (Gelişmiş)**
    -   Dış tedarikçi firmaların sistemde tanımlanması
    -   Otomatik bakım hatırlatmaları (asansör periyodik bakımı, yangın söndürme cihazları vb.)
    -   Maliyet analizi ve raporlama

### Aşama 4: Yasal Uyum, Raporlama ve Entegrasyonlar

1.  **E-Fatura / E-Serbest Meslek Makbuzu Entegrasyonu** (Türkiye)
    -   GİB API entegrasyonu ile e-fatura kesimi
    -   Arşivleme ve saklama süreleri takip sistemi
2.  **Dijital İmza ve Belge Yönetimi**
    -   E-imza / Mobil imza ile sözleşme onayı
    -   PDF üretme, belge versiyonlama
    -   Kişisel verilerin anonimleştirilmesi ve silme süreçleri (KVKK / GDPR uyumu)
3.  **Audit Log ve Denetim Mekanizmaları**
    -   Tüm CRUD işlemlerinde denetim kaydı tutulması
    -   Veri erişim raporları (kim, ne zaman, hangi veriyi görüntüledi/değiştirdi)
4.  **Performans ve Ölçeklenebilirlik İyileştirmeleri**
    -   Caching mekanizmaları (Redis, Memcached)
    -   CDN kullanımı (statik dosyalar, dokümanlar)
    -   Mikroservis mimarisine geçiş planı (ileride gerekli görülürse)

### Aşama 5: Sonraki Geliştirmeler ve Opsiyonel Özellikler

1.  **Etkinlik ve Toplantı Odası Rezervasyonları**
    -   Ortak alan rezervasyon modülü (toplantı odası, misafir süiti, bahçe kullanımı)
2.  **İş Zekası Panelleri**
    -   Power BI, Metabase gibi BI araçları ile entegrasyon
    -   Gelişmiş veri analitiği ve raporlar
3.  **Mobil Uygulama / Progressive Web App (PWA)**
    -   Sakinlerin kolay erişimi için mobil dostu arayüzler
    -   Push bildirimleri

## Süreç ve Versiyonlama

-   **Sürüm Yönetimi:**
    -   v0.1: Temel kullanıcı, site, aidat yönetimi
    -   v0.2: Otopark, spor salonu, kiracı yönetimi temelleri
    -   v0.3: Gelişmiş finansal raporlama, bakım-onarım, dil/para birimi desteği
    -   v0.4: Yasal entegrasyonlar (e-fatura), dijital imza, audit log
    -   v1.0: Stabil, entegre, tam fonksiyonel sistem
-   **Dokümantasyon:**
    -   Her modül için ayrı README veya doc dosyası
    -   API uç noktaları için OpenAPI/Swagger dokümantasyonu
    -   Erişim yetkileri, rol bazlı izinlerin net açıklamaları

## Sonuç

Bu doküman, proje geliştirme sürecinde bir yol haritası olarak kullanılmak üzere hazırlanmıştır. İlk etapta temel özellikler uygulanarak kısa sürede kullanıma hazır bir temel ürün oluşturmak (MVP), daha sonra kademeli olarak fonksiyonların genişletilmesi ve iyileştirilmesi hedeflenmektedir. Geliştirme ilerledikçe bu doküman güncellenmeli, her aşama tamamlandığında yeni özelliklerin entegre edileceği bir plan dahilinde sürüm yükseltmeleri yapılmalıdır.

# 
