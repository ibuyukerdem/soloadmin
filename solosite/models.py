# solosite/models.py
from django.db import models
from accounts.models import UserProfile
from common.models import AbstractBaseModel

class SiteRole(models.Model):
    """
    solosite uygulamasına özgü roller:
    Örneğin: admin, manager, staff
    """
    name = models.CharField(max_length=50, help_text="Rol adı (admin, manager, staff, vb.)")
    code = models.CharField(max_length=50, unique=True, help_text="Benzersiz rol kodu")

    def __str__(self):
        return self.name

class SiteUserRole(models.Model):
    userProfile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="solositeRoles"
    )
    role = models.ForeignKey(
        SiteRole,
        on_delete=models.CASCADE,
        related_name="assignedProfiles"
    )

    class Meta:
        unique_together = ("userProfile", "role")

    def __str__(self):
        return f"{self.userProfile.user.username} -> {self.role.name}"



class SitePermission(models.Model):
    code = models.CharField(max_length=100, unique=True, help_text="İzin kodu: örn solosite.view_apartment")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.code

class SiteRolePermission(models.Model):
    role = models.ForeignKey(SiteRole, on_delete=models.CASCADE, related_name="rolePermissions")
    permission = models.ForeignKey(SitePermission, on_delete=models.CASCADE, related_name="rolePermissions")

    class Meta:
        unique_together = ("role", "permission")

