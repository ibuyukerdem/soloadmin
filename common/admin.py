from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import GoogleApplicationsIntegration, SiteSettings, SmsSettings, SmtpSettings, WhatsAppSettings, CustomUser


# Özelleştirilmiş form açıklamaları (opsiyonel)
def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    form.base_fields['code'].help_text = "Para birimi kodunu girin. Örn: 'USD', 'EUR', 'TRY'."
    form.base_fields['name'].help_text = "Para biriminin tam adını girin. Örn: 'ABD Doları', 'Avro', 'Türk Lirası'."
    form.base_fields[
        'exchange_rate'].help_text = "1 birimin varsayılan para birimine karşılık gelen değerini girin. Örn: 1 USD = 20.000000 TL"
    form.base_fields[
        'is_default'].help_text = "Bu işaretlendiğinde, seçilen para birimi sistemin varsayılan para birimi olur."
    return form


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        help_texts = {
            'isDealer': "Bu kullanıcı bir bayiyse işaretleyin. Bayilere özel kampanyalar ve ek iskontolar uygulanabilir.",
            'dealer_segment': "Bayiyi hangi bayi segmentine dahil etmek istediğinizi seçin. Segmentler, özel fiyatlandırma ve kampanyalar için kullanılır.",
        }


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email'),
            'description': _('Kullanıcı adı, şifre ve e-posta bilgileri'),
        }),
        (_('Kişisel Bilgiler'), {
            'fields': (
                'first_name', 'last_name',
                'phoneNumber', 'mobilePhone', 'address', 'postalCode',
                'city', 'district', 'country', 'dateOfBirth', 'profilePicture',
                'isIndividual', 'identificationNumber', 'taxOffice', 'companyName',
                'isEfatura', 'secretQuestion', 'secretAnswer', 'smsPermission',
                'digitalMarketingPermission', 'kvkkPermission', 'selectedSite',
                'dealerID', 'dealer_segment', 'isDealer', 'discountRate',
                'timezone', 'preferred_language'
            ),
            'description': _('Kişiye ait detaylı bilgiler'),
        }),
        (_('Yetkiler'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': _('Sisteme giriş, yetkilendirme ve gruplar'),
        }),
        (_('Önemli Tarihler'), {
            'fields': ('last_login', 'date_joined'),
            'description': _('Kullanıcının giriş ve kayıt tarihleri'),
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'isDealer', 'selectedSite'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'companyName')
    ordering = ('username',)
    # Django'nın default UserAdmin'inde last_login ve date_joined sadece okunabilir olarak ayarlanır:
    readonly_fields = ('last_login', 'date_joined')


class WhatsAppSettingsAdmin(admin.ModelAdmin):
    """
    WhatsApp Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = ('site', 'apiUrl', 'phoneNumber', 'kontorMiktari', 'createdAt', 'updatedAt')
    list_filter = ('site', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'apiUrl', 'phoneNumber')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'apiUrl', 'phoneNumber', 'apiKey', 'kontorMiktari')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )


admin.site.register(WhatsAppSettings, WhatsAppSettingsAdmin)


class SmtpSettingsAdmin(admin.ModelAdmin):
    """
    SMTP Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = (
        'site',
        'emailAddress',
        'smtpServer',
        'smtpPort',
        'username',
        'useTls',
        'useSsl',
        'createdAt',
        'updatedAt'
    )
    list_filter = ('site', 'useTls', 'useSsl', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'emailAddress', 'smtpServer', 'username')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'emailAddress', 'smtpServer', 'smtpPort', 'username', 'password', 'useTls', 'useSsl')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )


admin.site.register(SmtpSettings, SmtpSettingsAdmin)


class SmsSettingsAdmin(admin.ModelAdmin):
    """
    SMS Ayarlarını admin panelinde yönetmek için özelleştirilmiş yapı.
    """
    list_display = ('site', 'url', 'username', 'kontorMiktari', 'createdAt', 'updatedAt')
    list_filter = ('site', 'createdAt', 'updatedAt')
    search_fields = ('site__domain', 'username', 'url')
    readonly_fields = ('createdAt', 'updatedAt')
    fieldsets = (
        (None, {
            'fields': ('site', 'url', 'username', 'password', 'kontorMiktari')
        }),
        ('Zaman Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
        }),
    )


admin.site.register(SmsSettings, SmsSettingsAdmin)


@admin.register(GoogleApplicationsIntegration)
class GoogleApplicationsIntegrationAdmin(admin.ModelAdmin):
    list_display = ('site', 'applicationType', 'createdAt', 'updatedAt')
    list_filter = ('applicationType', 'createdAt', 'updatedAt')
    search_fields = ('applicationType', 'site__name', 'applicationCode')
    ordering = ('-createdAt',)
    fieldsets = (
        (None, {
            'fields': ('site', 'applicationType', 'applicationCode')
        }),
        ('Tarih Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site', 'siteName', 'phone', 'gsm', 'email', 'updatedAt')
    list_filter = ('site', 'updatedAt')
    search_fields = ('site__name', 'siteName', 'email', 'phone', 'address')
    ordering = ('-updatedAt',)
    fieldsets = (
        ('Site Bilgileri', {
            'fields': ('site', 'siteName', 'metaTitle', 'metaDescription', 'logo')
        }),
        ('İletişim Bilgileri', {
            'fields': ('phone', 'gsm', 'email', 'address', 'googleMap')
        }),
        ('Politika ve Sözleşmeler', {
            'fields': ('cookiePolicy', 'privacyPolicy', 'termsOfUse', 'kvkkAgreement')
        }),
        ('Hakkımızda', {
            'fields': ('aboutUs',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')
