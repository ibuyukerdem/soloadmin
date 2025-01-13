from django.shortcuts import render

def has_site_permission(user, permission_code):
    # user -> request.user yani CustomUser
    # Bu fonksiyon siteye özgü bir izni kontrol eder.
    if not user.is_authenticated:
        return False

    # user.profile üzerinden SiteUserRole'ları çek
    user_profile = user.profile
    roles = user_profile.siteUserRoles.all().select_related('role')
    # Kullanıcının rollerindeki izinleri bul
    user_permission_codes = set()
    for user_role in roles:
        # İlgili role ait permissionları topla
        perms = user_role.role.rolePermissions.all().select_related('permission')
        for perm in perms:
            user_permission_codes.add(perm.permission.code)

    return permission_code in user_permission_codes


from rest_framework.permissions import BasePermission

class CanViewApartment(BasePermission):
    def has_permission(self, request, view):
        return has_site_permission(request.user, "solosite.view_apartment")
