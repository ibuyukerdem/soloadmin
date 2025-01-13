from django.contrib import admin

from accounts.models import UserProfile, UserSite


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    UserProfile modelini admin arayüzünde yönetmek için.
    Kullanıcının profil bilgileri (örneğin bio) üzerinde listeleme, arama ve
    ileride filtreleme desteği sunar.
    """

    list_display = ("user", "bio")
    search_fields = ("user__username", "bio")

    # fieldsets yapısı ile, ilgili alanları bir başlık altında toplayıp
    # description parametresiyle ek açıklamalar ekleyebiliyoruz.
    fieldsets = (
        (None, {
            "fields": ("user", "bio"),
            "description": (
                "Proje genelinde geçerli olabilecek ek profil alanları: "
                "Örneğin global roller, vb. ileride eklenebilir. "
                "(Farklı uygulamalara ait roller, alt uygulamalar içinde tanımlanacak.)"
            ),
        }),
    )


@admin.register(UserSite)
class UserSiteAdmin(admin.ModelAdmin):
    """
    Kullanıcı ile belirli bir site arasındaki ilişkiyi Django Admin'de yönetmek için.
    Kullanıcı-Site kaydını listeleyip, arama ve filtreleme gibi işlevler sunar.
    """
    list_display = ("user", "site", "role", "createdAt", "updatedAt")

    search_fields = ("user__username", "site__name")

    list_filter = ("role",)

    fieldsets = (
        ("Kullanıcı-Site Bilgisi", {
            "fields": ("user", "site", "role"),
            "description": (
                "Bu bölümde kullanıcının hangi sitede hangi rolde olduğunu belirleyebilirsiniz. "
                "Aynı kullanıcı, aynı siteye birden fazla kez eklenemeyeceği için "
                "<em>unique_together = (\"user\", \"site\")</em> kısıtlaması mevcuttur."
            ),
        }),
    )