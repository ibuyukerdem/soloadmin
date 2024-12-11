from rest_framework import serializers

from common.models import GoogleApplicationsIntegration, SiteSettings



class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site', 'siteName', 'metaTitle', 'metaDescription', 'logo',
            'cookiePolicy', 'privacyPolicy', 'termsOfUse', 'phone', 'gsm',
            'email', 'address', 'googleMap', 'aboutUs', 'kvkkAgreement',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']

class GoogleApplicationsIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleApplicationsIntegration
        fields = [
            'id', 'site', 'applicationType', 'applicationCode', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']
