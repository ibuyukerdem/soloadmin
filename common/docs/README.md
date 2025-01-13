# common Uygulaması Hakkında

-   common uygulaması, tüm projede ortak olarak kullanılabilecek soyut modeller, yardımcı fonksiyonlar, paylaşılan lojik ve alt yapıları barındırır.
-   Burada AbstractBaseModel gibi soyut modeller bulunabilir. Bu modeller, createdAt, updatedAt, site gibi alanları tüm modellerinize ekleyen ortak bir temel sağlar.
-   Ortak bileşenleri common içinde tutarak kod tekrarını azaltır ve proje geneline uyumlu bir yapı elde edersiniz.
-   common içinde gerekirse soyut bir AbstractRole modeli de tanımlayıp, uygulamaya özgü rol modellerinin bu soyut yapıdan türemesini sağlayabilirsiniz. Bu sayede her uygulamada rol kurgusunun temeli aynı soyutlamayı kullanır.
-   Kısaca common, projede çapraz kullanılacak araçların, soyutlamaların ve temel yapı taşlarının evidir. Her uygulama common’daki bileşenlerden faydalanarak tutarlı bir mimari ile geliştirilir.
-   Bu yaklaşım sayesinde kullanıcılarınız, profilleri ve izin sisteminiz tek bir altyapı üzerinden yönetilir. Yeni uygulamalar ekledikçe sadece o uygulamanın rol ve izin modellerini common ve accounts yapısına entegre ederek ölçeklendirebilirsiniz.

## AbstractBaseModel

AbstractBaseModel tüm modeller için şu alanları sağlar:

-   `site`: Hangi siteye ait olduğunu belirtir (`ForeignKey(Site)`).
-   `created_at`: Oluşturulma tarihi.
-   `updated_at`: Son güncellenme tarihi.

**Nasıl Kullanılır?**

```python
from common.models import AbstractBaseModel

class ExampleModel(AbstractBaseModel):
    name = models.CharField(max_length=255)
```
