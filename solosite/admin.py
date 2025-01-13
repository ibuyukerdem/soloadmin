from django.contrib import admin
from .models import SiteRole, SiteUserRole, SitePermission, SiteRolePermission

@admin.register(SiteRole)
class SiteRoleAdmin(admin.ModelAdmin):
    """
    SiteRole modelini yönetmek için admin arayüzü.
    Rolün ismi ve kodu üzerinde arama ve listeleme imkânı sunar.
    """
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(SiteUserRole)
class SiteUserRoleAdmin(admin.ModelAdmin):
    """
    SiteUserRole modelini yönetmek için admin arayüzü.
    Kullanıcı rol atamalarını, kullanıcı ismine ve role göre listeleyip filtrelemeyi sağlar.
    """
    list_display = ("userProfile", "role")
    search_fields = ("userProfile__user__username", "role__name")
    list_filter = ("role",)


@admin.register(SitePermission)
class SitePermissionAdmin(admin.ModelAdmin):
    """
    SitePermission modelini admin arayüzünde yönetmek için.
    İzin koduna ve açıklamasına göre arama imkânı sunar.
    """
    list_display = ("code", "description")
    search_fields = ("code", "description")

@admin.register(SiteRolePermission)
class SiteRolePermissionAdmin(admin.ModelAdmin):
    """
    SiteRolePermission modelini admin arayüzünde yönetmek için.
    Rol ve izin bilgilerini listeleyip arama ve filtreleme yapmayı sağlar.
    """
    list_display = ("role", "permission")
    search_fields = ("role__name", "permission__code")
    list_filter = ("role",)