# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

# create_docs_structure.py

`create_docs_structure.py` dosyası, Django projeleri için dokümantasyon yapısını hızlı ve düzenli bir şekilde oluşturmayı sağlayan bir araçtır. Her bir app ve sub-app için gerekli dokümantasyon dosyalarını oluşturur ve bunlara başlangıç içerikleri ekler.

---

## Özellikler

- **Kök Dizin Dokümantasyonu**: Proje genelini tanımlayan root-level `docs` dizinini oluşturur ve gerekli dosyaları (`README.md`, `API_REFERENCE.md`, vb.) ekler.
- **App ve Sub-App Dokümantasyonu**: Her app ve sub-app için ayrı bir `docs` dizini oluşturur ve app'e özgü içerikleri ekler.
- **Hata Dayanıklılığı**: Var olan dosyaları bozmadan, yeni içerikleri ekler ve eski içerikleri korur.
- **UTF-8 Formatı**: Tüm dosyalar UTF-8 formatında yazılır.
- **Otomatik Metadata Çekme**: `apps.py` dosyasından `verbose_name` ve `description` bilgilerini alır.
- **Kullanıcı Dostu Arayüz**: Etkileşimli bir seçenek sunar:
  - `0`: Root-level dokümantasyon oluştur.
  - `1`: Belirtilen bir app için dokümantasyon oluştur.
  - `2`: Belirtilen bir app'in sub-app'leri için dokümantasyon oluştur.

---

## Kullanım

### Komut Satırından Çalıştırma

1. **Script'i Çalıştırın:**
   ```bash
   python create_docs_structure.py
Seçenekler:

0: Root-level dokümantasyon oluşturur.
1: Belirtilen bir app için dokümantasyon oluşturur.
2: Belirtilen bir app ve sub-app'leri için dokümantasyon oluşturur.
Örnek Kullanım:

Root-level dokümantasyon için:
scss
Kodu kopyala
Seçiminizi yapın (0/1/2): 0
App için dokümantasyon:
scss
Kodu kopyala
Seçiminizi yapın (0/1/2): 1
App adını girin: soloaccounting
Sub-app için dokümantasyon:
yaml
Kodu kopyala
Seçiminizi yapın (0/1/2): 2
Ana app adını girin: soloaccounting
Sub-app adlarını virgülle ayırarak girin: reports, analytics
Oluşturulan Dizin Yapısı
Her çalıştırmada aşağıdaki yapı oluşturulur:

bash
Kodu kopyala
docs/
├── README.md                # Proje genel bilgileri
├── DEVELOPERS_GUIDE.md      # Geliştirici rehberi
├── API_REFERENCE.md         # Tüm API endpoint'leri
├── APPS_OVERVIEW.md         # App ve sub-app açıklamaları
├── FRONTEND_GUIDE.md        # Frontend geliştiriciler için rehber
App veya sub-app dokümantasyonu için:

rust
Kodu kopyala
app_name/
├── docs/
│   ├── README.md            # App'e özgü bilgiler
│   ├── API_REFERENCE.md     # App'e özgü API endpoint'leri
Dosyalar ve İçerikler
1. README.md
Projenin genel bilgilerini içerir. Örnek içerik:

markdown
Kodu kopyala
# Proje Dokümantasyonu

Bu proje Django tabanlı bir uygulamadır.
2. DEVELOPERS_GUIDE.md
Geliştiriciler için bir rehber sunar. Kod yapısı, test süreçleri ve en iyi uygulamalar hakkında bilgi içerir.

3. API_REFERENCE.md
API endpoint'lerini açıklar. Örnek içerik:

markdown
Kodu kopyala
# API Referansı

Tüm API endpoint'leri ve açıklamaları burada yer alır.
4. APPS_OVERVIEW.md
Projede bulunan tüm app'leri ve sub-app'leri listeler. Örnek içerik:

markdown
Kodu kopyala
# App ve Sub-App Açıklamaları

- soloaccounting: Sub-app bulunmuyor
- soloblog: reports, analytics
Sıkça Sorulan Sorular (FAQ)
Hangi durumlarda mevcut dosyalar korunur?

Eğer dokümantasyon dosyaları zaten mevcutsa, yeni içerikler dosyanın sonuna eklenir ve mevcut içerikler korunur.
Hangi formatlarda dosyalar yazılır?

Tüm dosyalar UTF-8 formatında yazılır.
apps.py içeriği eksikse ne olur?

Eğer apps.py içinde verbose_name veya description tanımlanmamışsa, boş değerler atanır.
Sub-app dokümantasyonu nasıl oluşturulur?

2 seçeneği seçildiğinde, belirtilen sub-app'ler için README.md ve API_REFERENCE.md dosyaları oluşturulur.
Hata Ayıklama
Hata: apps.py bulunamadı.

Çözüm: App'in kök dizininde bir apps.py dosyası olduğundan emin olun.
Hata: AppConfig sınıfı içinde bulunamadı.

Çözüm: apps.py içinde bir AppConfig sınıfı tanımlı olduğundan emin olun ve verbose_name ile description alanlarını ekleyin.
Hata: Dosya oluşturulamıyor.

Çözüm: Script'in çalıştığı dizinde yazma izni olduğundan emin olun.
Geliştirme ve Katkı
Bu script'i daha da geliştirmek için:

Yeni dokümantasyon şablonları ekleyebilirsiniz.
Sub-app dokümantasyonu için daha ayrıntılı içerik sağlayabilirsiniz.
Katkıda bulunmak için:

Script'i fork edin.
Yeni özellikler ekleyin.
Bir pull request gönderin.


# API Yapılandırma Aracı create_api_structure.py

Bu araç, Django uygulamaları için hızlı bir şekilde temel API dosya yapısını oluşturur.

## Ne İşe Yarar?
- Belirttiğiniz uygulama veya alt uygulama için `api` dizini oluşturur.
- `__init__.py`, `urls.py`, `views.py` ve `serializers.py` dosyalarını otomatik olarak ekler.
- Django REST Framework için başlangıç şablonları içerir.

## Nasıl Kullanılır?
1. Betiği çalıştırmak için aşağıdaki komutu kullanın:
   ```bash
   python create_api_structure.py app_adi
   python create_api_structure.py app_adi/alt_uygulama


---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.


# Versiyon Artırma İşlemi

Kurulum tamamlandıktan sonra, app'lerinizin `__version__` değerlerini artırmak için aşağıdaki komutları kullanabilirsiniz:

## Patch Güncellemesi (Küçük değişiklikler)

```bash
bump2version patch
Örnek: 0.1.0 → 0.1.1

Minor Güncellemesi (Yeni özellik ekleme)
bump2version minor
Örnek: 0.1.0 → 0.2.0

Major Güncellemesi (Büyük değişiklikler veya kırılma noktaları)

bump2version major
Örnek: 0.1.0 → 1.0.0

## Sürümleme Prensipleri

Semantik Versiyonlama (Semantic Versioning) prensiplerini uygulayarak, versiyon numaralarının anlamlı olmasını sağlayabilirsiniz.

## Örneğin:
- **MAJOR versiyon (1.0.0 → 2.0.0):**  
  Geriye dönük uyumsuz API değişiklikleri.

- **MINOR versiyon (1.1.0 → 1.2.0):**  
  Geriye dönük uyumlu yeni özellikler.

- **PATCH versiyon (1.1.1 → 1.1.2):**  
  Geriye dönük uyumlu hata düzeltmeleri.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.

---

# Geliştirici Rehberi

Kod yapısı ve test süreçleri burada açıklanır.