# solosurvey Uygulaması Geliştirici Notları

Genel Amaç solosurvey uygulaması, birden fazla siteye hizmet veren bir anket yönetim sistemi oluşturur. Her site kendi anketlerini, sorularını, seçeneklerini, tetikleyicilerini ve yanıtlarını yönetebilir. Bu yapı sayesinde her siteye özgün müşteri memnuniyeti anketleri sunmak, kullanıcı deneyimini ölçmek ve bu sonuçları raporlamak mümkündür.

## Temel Özellikler Çoklu Site Desteği:

Tüm modeller, AbstractBaseModel üzerinden site ile ilişkilendirilir. Böylece her kayıt spesifik bir siteye aittir. Anket Yönetimi (Survey): Her bir Survey (Anket), bir siteye ait başlık, açıklama, aktiflik durumu, başlangıç ve bitiş tarihleri, ödül puanı gibi özelliklerle tanımlanır.

## Soru ve Seçenekler (Question, Choice):

Bir anketin içeriğini oluşturan sorular ve çoktan seçmeli/tek seçimli sorulara ait seçenekler.

## Tetikleyiciler (SurveyTrigger):

Anketlerin belirli olaylardan sonra otomatik olarak devreye girmesini sağlar (örn. sipariş tamamlandığında müşteriye anket linki gönderme).

## Yanıtlar (SurveyResponse, Answer):

Kullanıcıların veya anonim katılımcıların anketleri yanıtlarken verdiği cevaplar. Bu sayede sonuçlar analiz edilebilir. Modeller Arası İlişkiler Survey -\> Question: Bir anket birden çok soruya sahip olabilir. Question -\> Choice: Bir soru birden çok seçeneğe sahip olabilir (eğer soru çoktan seçmeli ise). Survey -\> SurveyTrigger: Bir anket birden çok tetikleyiciye sahip olabilir. Survey -\> SurveyResponse -\> Answer: Her anketin birden çok yanıtı, her yanıtın da sorulara karşı verilen birden çok cevabı (answer) olabilir. API Tasarımı Viewset ve Serializer’lar: SurveyViewSet, SurveyTriggerViewSet, SurveyResponseViewSet gibi ViewSet’ler RESTful endpoint’ler sunar. Bu sayede Next.js veya başka bir frontend client’ı kolayca entegre olabilir. Filtreleme ve Yetkilendirme: AbstractBaseViewSet kullanıcıların sadece yetkili oldukları site ile ilgili kayıtlar üzerinde işlem yapmasını sağlar. Bu mekanizma User.selectedSite üzerinden kontrol edilir. Serileştirme: SurveySerializer, QuestionSerializer, ChoiceSerializer, SurveyTriggerSerializer ve SurveyResponseSerializer anket verilerini JSON formatında sunar ve alır. Bu sayede veriler frontend katmanına net, anlaşılır ve işlenebilir halde iletilir.

## Genişletilebilirlik Yeni Soru Tipleri:

Question modelindeki questionType alanına yeni soru tipleri ekleyebilirsiniz. Ardından ilgili frontend komponenti ve serializer mantıklarını da genişleterek esnek bir soru seti sunabilirsiniz.

## Ödül Sistemi:

rewardPoints üzerinden temel bir ödül mekanizması bulunur. Bunu genişleterek yanıtlayan kullanıcılara puan biriktirme, puanları kupon veya indirimlere dönüştürme gibi ek özellikler ekleyebilirsiniz.

## Bildirim Kanalları:

SurveyTrigger modeli üzerinden tetikleyici olaylarda e-posta, SMS veya WhatsApp gönderimi planlanmıştır. İhtiyaç durumunda yeni bildirim kanalları eklenebilir veya mevcut kanalların entegrasyonları geliştirilebilir.

## Raporlama ve Analitik:

SurveyResponse ve Answer modelleri raporlamaya elverişlidir. Bu verileri kullanarak ek rapor endpoint’leri geliştirebilir veya üçüncü parti analitik araçları entegre edebilirsiniz.

## Bakım, Test ve Performans Testler:

Unit test ve integration test’lerinizi hem modeller hem de viewset’ler için yazmanız tavsiye edilir. Bu sayede uygulama davranışından emin olabilir, değişiklikler sonrasında regresyonları önleyebilirsiniz.

## Performans İyileştirme:

Çok sayıda anket, soru, yanıt barındıran durumlarda veritabanı sorgularını optimize etmek, index’ler eklemek veya caching mekanizması kurmak gerekebilir.

## Güncellemeler ve Sinyaller:

Anket cevaplanınca otomatik puan ekleme veya mail gönderme gibi işlemler için Django sinyalleri (post_save) kullanılabilir. Bu yaklaşım, kodunuzu modüler ve bakımı kolay hale getirir. Entegrasyon Notları

## Ortak Ayarlar (SMTP, SMS, WhatsApp):

common uygulamasındaki SmtpSettings, SmsSettings, WhatsAppSettings modelleri aracılığıyla anket tetikleyicileri belirli iletişim kanallarında otomatik mesaj gönderebilir.

## Front-end ile İletişim:

Next.js tabanlı bir ön yüz ile JWT veya Session tabanlı kimlik doğrulama kullanarak DRF endpoint’lerine bağlanabilirsiniz. Sunulan endpoint’lerden anketleri çekip, anketleri doldurup, cevapları post edebilirsiniz.
