from common.models import AbstractBaseModel
from django.db import models

# Model Açıklaması:
# Bu model, projemizdeki her veri kaydının bir siteyle ilişkilendirilmesini sağlamak için
# `common.models.AbstractBaseModel` sınıfını miras alır. Bu sınıf, aşağıdaki alanları içerir:
# 1. `site`: Kaydın hangi siteye ait olduğunu belirtir (`ForeignKey(Site)`).
# 2. `created_at`: Kaydın oluşturulma tarihi (`DateTimeField`).
# 3. `updated_at`: Kaydın son güncellenme tarihi (`DateTimeField`).
#
# AbstractBaseModel kullanılarak, tekrarlayan kodlar minimize edilmiş ve verilerin çoklu site
# desteği için yapılandırılması sağlanmıştır.

# class ExampleModel(AbstractBaseModel):
#     """
#     Örnek model, AbstractBaseModel'i miras alarak `site`, `created_at` ve `updated_at` alanlarına sahiptir.
#     """
#     name = models.CharField(max_length=255, help_text="Modelin adı")
#     description = models.TextField(help_text="Modelin açıklaması")
#
#     def __str__(self):
#         return self.name