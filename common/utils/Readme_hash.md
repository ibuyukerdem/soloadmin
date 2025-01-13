https://chatgpt.com/g/g-p-675dc2728ffc81919a0cb562da6798e0-soloadmin/c/675df438-f0a0-8006-a02a-9bbc93ac4ef8

# **Proje Notları**

Bu dosya, proje geliştirme sürecinde alınan notları, yapılan işlemleri ve önemli noktaları içermektedir.

---

## **1. Proje Genel Yapısı**

- **Amaç:**
  - Kullanıcı işlemlerini güvenli bir şekilde loglamak.
  - Zincir yapısıyla kayıt bütünlüğünü sağlamak.
  - Adli gerekliliklere uygun, detaylı kullanıcı bilgileri toplamak.

- **Proje Modülleri:**
  - **Loglama Sistemi:** Kullanıcı eylemlerini kayıt altına alır.
  - **Hash Zinciri:** Logların zincirleme kontrolünü sağlar.
  - **Periyodik Görevler:** Zinciri düzenli aralıklarla doğrular.

---

## **2. Geliştirme Sürecinde Yapılan İşlemler**

### **2.1. Loglama Sistemi**
- `LogEntry` modeli oluşturuldu.
  - Kullanıcı işlemleri için `user`, `ip_address`, `browser`, `operating_system` gibi detaylar eklendi.
  - Zincir yapısı için `hashed_data` ve `previous_hashed_data` alanları eklendi.
  - `timestamp` alanı ile işlem zamanı kaydedildi.

- Kullanıcı bilgilerini çıkarmak için `get_user_info` fonksiyonu oluşturuldu (`user_info_extractor.py`).

- **Test İşlemleri:**
  - `test_log_action` fonksiyonu ile loglama sistemi test edildi.

---

### **2.2. Hash Zinciri Yönetimi**
- `hash_key_manager.py` dosyasında `get_key_for_timestamp` fonksiyonu oluşturuldu.
  - Dinamik hash anahtarı, her 15 dakikada bir değişen yapıda tasarlandı.
  - Anahtar `timestamp` üzerinden hesaplanarak her kayıt için özelleştirildi.

- Hash zinciri doğrulama için `hash_chain_verifier.py` oluşturuldu.
  - `verify_chain` fonksiyonu ile zincir bozulmaları tespit edildi.

---

### **2.3. Periyodik Görevler**
- Zincir doğrulama işlemleri Celery ile otomatik hale getirildi.
  - `verify_all_sites` görevi, tüm sitelerde zinciri düzenli olarak kontrol eder.

---

## **3. Test Süreci**

- Loglama sistemi ve zincir doğrulama, manuel testler ile başarıyla doğrulandı.
- **Komut:**
  ```bash
  python manage.py test_logging


Çıktı:
- mathematica
- Kodu kopyala
- Log testi başlatılıyor...
- Mevcut site kaydı kullanılıyor.
- Log oluşturuldu: 1
- Log testi tamamlandı.


## **4. Önemli Notlar**

### **4.1. Veritabanı Ayarları**
- `Site` tablosunda aynı domain'e sahip kayıtlar olmamalıdır.
- `get_or_create` yöntemi kullanılarak tekrar eden kayıtlar önlenir:
  ```python
  site, created = Site.objects.get_or_create(
      domain='example.com',
      defaults={'name': 'Example Site'}
  )

### **4.2. Ortam Değişkenleri (.env)**

Aşağıdaki ortam değişkenlerini `.env` dosyasına ekleyerek projenin düzgün çalışmasını sağlayabilirsiniz:

```env
HASH_PERIOD_SECONDS=900                # Hash anahtarı periyodu (15 dakika)
STATIC_SALT_FOR_HASH_KEY=your_salt     # Hash için kullanılan sabit tuz
CELERY_BROKER_URL=redis://localhost:6379/0  # Celery için Redis broker URL


### **4.3. Celery Konfigürasyonu**

Celery, zincir doğrulama işlemlerini otomatik hale getirmek için kullanılan görev yöneticisidir. Periyodik zincir kontrolü ve diğer zamanlanmış görevler için Celery Worker ve Beat süreçlerini çalıştırmanız gerekmektedir.

#### **Başlatma Komutları**

1. **Celery Worker Başlatma**  
   Zincir doğrulama işlemleri için çalışan süreci başlatmak için aşağıdaki komutu kullanın:

   ```bash
   celery -A projeler worker --loglevel=info


Görevlerin Zamanlanması
Zincir doğrulama işlemi, common/tasks.py dosyasında tanımlanmıştır. Görev periyodik olarak 15 dakikada bir çalıştırılır.
Görev Tanımı: verify_all_sites
Görev Dosyası: common/tasks.py
Tanım: Zincirin doğruluğunu kontrol eder ve bozulmaları tespit eder.

common/
├── api/
├── docs/
├── migrations/
├── utils/
│   ├── __init__.py                # "utils" klasörünü Python paketi olarak tanımlar
│   ├── hash_key_manager.py        # Dinamik hash anahtarlarını yöneten sınıf
│   ├── user_info_extractor.py     # Kullanıcı tarayıcı, işletim sistemi ve IP bilgilerini çıkarır
│   ├── logging_helper.py          # Loglama işlemleri ve test fonksiyonları
│   ├── hash_chain_verifier.py     # Hash zinciri doğrulama işlemleri
├── __pycache__/                   # Python önbellek dosyaları
├── admin.py                       # Django admin arayüzü için ayarlar
├── apps.py                        # Uygulama ayarları
├── models.py                      # Loglama ve hash zinciri için modeller
├── tasks.py                       # Celery görevlerini tanımlayan dosya
├── tests.py                       # Test işlemleri için dosya
├── views.py                       # Görünüm fonksiyonları ve API'ler
└── __init__.py                    # Uygulamayı Python paketi olarak tanımlar


Alt Sınıfta create Metodu Tanımlı
Eğer alt sınıfta create metodu tanımlanmışsa, aşağıdaki gibi super().create() ile üst sınıfın işlemlerini çağırabilirsiniz:

python
Kodu kopyala
from common.views import AbstractBaseViewSet
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(AbstractBaseViewSet):
    """
    Ürün modeline ait CRUD işlemleri için ViewSet.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        """
        Alt sınıfta create metodu.
        - Üst sınıftaki loglama işlemleri korunur.
        - Ek işlevler eklenir.
        """
        # Üst sınıftaki create işlemini çağır
        response = super().create(request, *args, **kwargs)

        # Ek bir işlem: Örneğin, bildirim gönder
        print("Yeni ürün oluşturuldu: ", response.data)

        return response
