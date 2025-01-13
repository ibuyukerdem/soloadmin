# accounts/models.py

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from common.models import AbstractBaseModel

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    # Proje genelinde geçerli olabilecek ek profil alanları:
    bio = models.TextField(blank=True, null=True)  # Örnek olarak

    # Örneğin global roller, vb. ileride eklenebilir.
    # (Farklı uygulamalara ait roller, alt uygulamalar içinde tanımlanacak.)

    def __str__(self):
        return f"{self.user.username} - Profile"


# kullanıcıların belirli sitelerle olan ilişkisi burada tanımlıyoruz
ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('USERS', 'Users'),
    ('OPERATION', 'Operation'),
)

# accounts/models.py
class UserSite(AbstractBaseModel):
    """
    Kullanıcının belirli bir site ile ilişkisi ve o sitedeki rolü.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userSites",
        verbose_name="Kullanıcı"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='USERS',
        help_text="Kullanıcının bu site üzerindeki rolü."
    )

    class Meta:
        verbose_name = "Kullanıcı-Site İlişkisi"
        verbose_name_plural = "Kullanıcı-Site İlişkileri"
        unique_together = ("user", "site")  # Tercih edilebilir, aynı user-site çiftini engellemek için

    def __str__(self):
        return f"{self.user.username} - {self.site.name} ({self.role})"
