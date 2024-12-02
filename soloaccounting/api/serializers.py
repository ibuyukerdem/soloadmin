from rest_framework import serializers

from soloaccounting.models import CustomUser


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
