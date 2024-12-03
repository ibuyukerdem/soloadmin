# Common Uygulaması

Bu uygulama, proje genelinde tekrar eden yapıların ve soyut modellerin tutulduğu yerdir.

## AbstractBaseModel

AbstractBaseModel tüm modeller için şu alanları sağlar:
- `site`: Hangi siteye ait olduğunu belirtir (`ForeignKey(Site)`).
- `created_at`: Oluşturulma tarihi.
- `updated_at`: Son güncellenme tarihi.

**Nasıl Kullanılır?**
```python
from common.models import AbstractBaseModel

class ExampleModel(AbstractBaseModel):
    name = models.CharField(max_length=255)
