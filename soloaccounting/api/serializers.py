from rest_framework import serializers

from soloaccounting.models import CustomUser, UserSite, ExtendedSite, Site, Product, SiteUrun, Menu


class ExtendedSiteSerializer(serializers.ModelSerializer):
    """
    Genişletilmiş Site modelinin serileştirilmesi için serializer sınıfı.
    """

    class Meta:
        model = ExtendedSite
        fields = ['isActive', 'isOurSite', 'isDefault', 'showPopupAd', 'logo', 'createdAt', 'updatedAt']


class SiteSerializer(serializers.ModelSerializer):
    """
    Django'nun Site modelini ve ExtendedSite ilişkisini serileştirmek için serializer.
    """
    extended_site = ExtendedSiteSerializer()

    class Meta:
        model = Site
        fields = ['id', 'domain', 'name', 'extended_site']


class UserSiteSerializer(serializers.ModelSerializer):
    site = SiteSerializer()
    products = serializers.SerializerMethodField()

    class Meta:
        model = UserSite
        fields = ['id', 'user', 'site', 'products', 'createdAt', 'updatedAt']
        read_only_fields = ['createdAt', 'updatedAt']

    def get_products(self, obj):
        # site.urunSite üzerinden product larına erişebilirsiniz.
        # OneToOneField olduğu için site'nin tek bir urunSite'sı vardır.
        urun_site = getattr(obj.site, 'urunSite', None)
        if urun_site:
            return [product.name for product in urun_site.urun.all()]
        return []


class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phoneNumber",
            "mobilePhone",
            "address",
            "postalCode",
            "city",
            "district",
            "country",
            "dateOfBirth",
            "profile_picture",
            "isIndividual",
            "companyName",
            "identificationNumber",
            "taxOffice",
            "isEfatura",
            "smsPermission",
            "digitalMarketingPermission",
            "kvkkPermission",
        ]

    def get_profile_picture(self, obj):
        if obj.profilePicture:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.profilePicture.url) if request else obj.profilePicture.url
        return None


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phoneNumber', 'isIndividual']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'serviceDuration', 'price', 'isActive', 'slug', 'createDate', 'updateDate']


class SiteUrunSerializer(serializers.ModelSerializer):
    urun_names = serializers.SerializerMethodField()

    class Meta:
        model = SiteUrun
        fields = ['id', 'site', 'urun', 'urun_names', 'createdAt']

    def get_urun_names(self, obj):
        return [urun.name for urun in obj.urun.all()]


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'title', 'path', 'icon', 'roles', 'caption', 'info', 'disabled', 'external', 'children'
        ]

    def get_children(self, obj):
        # Eğer obj herhangi bir öğenin parent'i değilse children None olmalı
        if obj.children.exists():
            user = self.context.get('request').user
            children = obj.children.all()
            if not user.is_superuser:
                children = children.filter(is_superuser_only=False)
            return MenuSerializer(children, many=True, context=self.context).data
        return None  # Parent olmayan öğeler için None döner

    def to_representation(self, instance):
        """
        Serializer çıktısını özelleştir.
        Eğer children alanı yoksa tamamen kaldır.
        """
        representation = super().to_representation(instance)

        # Eğer children None ise tamamen kaldır
        if not instance.children.exists():
            representation.pop('children', None)

        return representation
