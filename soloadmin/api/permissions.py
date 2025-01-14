# soloadmin/api/permissions.py
from rest_framework.permissions import BasePermission

class OnlyStaffCanSeeDocs(BasePermission):
    """
    Sadece staff (is_staff=True) kullanıcılar erişebilsin
    isterseniz superuser veya başka koşullar da ekleyebilirsiniz.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )
