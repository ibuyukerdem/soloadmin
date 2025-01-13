# Kullanıcı, Profil ve Rol-İzin Yönetimi Rehberi

**Bu belge, projenizin kullanıcı kimlik doğrulaması, kullanıcı profili yönetimi, rol ve izin yapısının nasıl kurgulandığını açıklar. Amacımız esnek, ölçeklenebilir ve uygulama bazlı rolleri destekleyen bir yapı kurmaktır.**

**Temel Bileşenler**

1.  **CustomUser (accounts/models.py)  
    Projedeki tüm kullanıcılar için temel doğrulama modeli. AbstractUser’dan türetilmiş olup kimlik doğrulama (login, password reset, vs.) işlevlerinin temelini oluşturur.**

**Örnek Alanlar:**

-   **username, email, password (Temel kimlik doğrulama alanları)**
    -   **phoneNumber, address, city, country gibi ek iletişim/demografik veriler**
    -   **preferred_language, timezone gibi kullanıcı tercihleri**
    -   **selectedSite gibi hangi site veya alanın aktif olarak seçildiği bilgisi**
1.  **UserProfile (accounts/models.py)  
    Her kullanıcıya ait genişletilmiş profil bilgilerini tutar.**
    -   **OneToOneField ile CustomUser modeline bağlıdır.**
    -   **Proje genelinde kullanıcıya ilişkin ortak bilgilere erişmek için tek bir profil kaynağı sunar.**
    -   **Rol ve izin ilişkileri bu profil üzerinden tanımlanır.**
2.  **Rol ve İzin Yapısı  
    Yerleşik Django Group ve Permission sistemini kullanmak yerine, burada daha esnek bir özel rol-izin yapısı kurguluyoruz. Her uygulama kendi rol ve izin modellerini oluşturur ve UserProfile üzerinden bu rolleri kullanıcıya atar.**

**Temel Kavramlar:**

-   **Role Modeli (Uygulama Bazlı): Her uygulama, kendi ihtiyaç duyduğu rolleri (admin, manager, staff, customer_service vb.) bir Role modeli ile tanımlar.**
    -   **Permission Modeli (Uygulama Bazlı): Her rolün hangi eylemlere veya verilere erişebileceğini belirlemek için bir Permission modeli tanımlanır. Bu izinler genellikle belirli kodlarla (solosite.view_apartment, solosite.edit_apartment gibi) ifade edilir.**
    -   **RolePermission İlişkisi: Bir rolün sahip olduğu izinler RolePermission modeliyle tanımlanır.**
    -   **UserProfile - Role İlişkisi: Kullanıcıya bir rol atamak için UserProfile ve Role arasında Many-to-Many veya aratablo yapısı kullanılır (örneğin SiteUserRole).**

**Dizayn ve Akış**

1.  **Kullanıcı Oluşturma:**
    -   **Yeni bir kullanıcı oluşturulduğunda CustomUser kaydı yapılır.**
    -   **Otomatik veya manuel olarak bu kullanıcıya bir UserProfile kaydı da oluşturulur.**
2.  **Rol Ekleme:**
    -   **Her uygulama (örnek: solosite) kendi Role modelini tanımlar.**
    -   **Aşağıda solosite uygulaması için örnek bir rol modeli gösterilmektedir.**

```
# solosite/models.py
from django.db import models
from accounts.models import UserProfile
from common.models import AbstractBaseModel

class SiteRole(AbstractBaseModel):
    name = models.CharField(max_length=50)  # Örn: "Admin"
    code = models.CharField(max_length=50, unique=True)  # Örn: "admin"

    def __str__(self):
        return self.name
```

### 

### 

### Role atamaları için bir ara tablo:

```
class SiteUserRole(models.Model):
    userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="siteUserRoles")
    role = models.ForeignKey(SiteRole, on_delete=models.CASCADE, related_name="assignedUsers")

    class Meta:
        unique_together = ("userProfile", "role")

    def __str__(self):
        return f"{self.userProfile.user.username} - {self.role.name}"
```

## **İzin Ekleme:**

### İlgili uygulamada izinleri belirlemek için bir Permission modeli tanımlayın:

```
# solosite/models.py
class SitePermission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # Örn: "solosite.view_apartment"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.code
```

### Rol-İzin ilişkisi:

```
class SiteRolePermission(models.Model):
    role = models.ForeignKey(SiteRole, on_delete=models.CASCADE, related_name="rolePermissions")
    permission = models.ForeignKey(SitePermission, on_delete=models.CASCADE, related_name="rolePermissions")

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} - {self.permission.code}"
```

### **Kullanıcının İzin Kontrolü:**

### Bir isteği işlerken kullanıcının belirli bir izne sahip olup olmadığını kontrol etmeniz gerekir.

### has_site_permission adında bir yardımcı fonksiyon örneği:

```
# Örneğin solosite/utils.py
def has_site_permission(user, permission_code):
    if not user.is_authenticated:
        return False
    user_profile = user.profile
    roles = user_profile.siteUserRoles.select_related('role').all()
    user_permission_codes = set()

    for user_role in roles:
        perms = user_role.role.rolePermissions.select_related('permission').all()
        for perm in perms:
            user_permission_codes.add(perm.permission.code)

    return permission_code in user_permission_codes
```

### Bir View içinde kullanımı (DRF örneği):

```
# solosite/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import has_site_permission

class ApartmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_site_permission(request.user, "solosite.view_apartment"):
            return Response(status=403, data={"detail": "İzniniz yok"})
        
        # İzin varsa daireleri listele
        apartments = ... # Apartment queryset
        # ...
        return Response(data=...)
```

### **Başlangıç Rehberi**

### accounts/models.py içerisinde CustomUser ve UserProfile modellerini tanımlayın. CustomUser projenin AUTH_USER_MODEL ayarında kullanılsın.

```
# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    # ... diğer alanlar
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    # Proje genelinde kullanılacak ek profil alanları
    def __str__(self):
        return self.user.username
```

### settings.py içinde:

```
AUTH_USER_MODEL = 'accounts.CustomUser'
```

### Uygulamaya özel roller ve izin modellerinizi ilgili uygulama içinde tanımlayın (örneğin solosite).

### Kullanıcılara rol vermek için SiteUserRole üzerinden kayıt ekleyin. Örneğin:

```
# Örnek kullanım
from accounts.models import UserProfile
from solosite.models import SiteRole, SiteUserRole

user_profile = UserProfile.objects.get(user__username="testuser")
admin_role = SiteRole.objects.get(code="admin")
SiteUserRole.objects.create(userProfile=user_profile, role=admin_role)
```

### İzin tanımlayıp rol-izin ilişkilerini belirleyin:

```
from solosite.models import SitePermission, SiteRolePermission

view_apartment_perm = SitePermission.objects.create(code="solosite.view_apartment")
SiteRolePermission.objects.create(role=admin_role, permission=view_apartment_perm)
```

### Artık testuser kullanıcısı admin rolüne ve solosite.view_apartment iznine sahip. İlgili endpointlere erişimde has_site_permission fonksiyonu üzerinden kontrol yapabilirsiniz.

### 

### 

### 

## Özet

### accounts uygulaması kullanıcı ve profil yönetiminin merkezi.

### UserProfile üzerinden her kullanıcıya ait ek bilgiler ve roller atanır.

### Her uygulama (örneğin solosite) kendi rol, izin ve bu ikisi arasındaki ilişkiyi yönetir.

### İzin kontrolleri proje genelinde tutarlı bir şekilde UserProfile üzerinden gerçekleşir.

### Bu yaklaşım, esnek bir yapıyla farklı uygulamaların kendi rol/izin sistemlerini tanımlamalarını, ancak tüm kullanıcı bilgisinin merkezi bir noktada (UserProfile) toplanmasını sağlar. Uygulamalar büyüdükçe veya yeni uygulamalar eklendikçe, yeni roller ve izinler kolayca entegre edilebilir.
