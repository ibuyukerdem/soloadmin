# accounts/signals.py

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from accounts.models import UserSite

@receiver(pre_save, sender=UserSite)
def handle_user_site_update(sender, instance, **kwargs):
    """
    Bir UserSite kaydı kaydedilmeden (save() öncesi) önceki kullanıcı (old_user)
    ile yeni kullanıcı (new_user) farklı ise:
      - Eski kullanıcıda başka site yoksa pasif yap (is_active=False), selectedSite=None.
      - Yeni kullanıcıyı aktif yap (is_active=True) ve selectedSite=instance.site.

    Senaryolar:
    1) YENİ KAYIT (Create):
       instance.pk = None -> "old_instance" çekilemez. Sadece "new_user" aktif hale getirilir.
    2) GÜNCELLEME (Update):
       instance.pk != None -> DB'den eski halini çekerek "old_user" ile "new_user" kıyaslarız.
         - old_user != new_user ise -> "site devri" mantığı devreye girer.
         - old_user'ın başka site kaydı yoksa -> pasif yapılır.
         - new_user -> aktif yapılır, selectedSite=instance.site.
    """
    old_user = None
    try:
        if instance.pk:
            # Kayıt güncelleniyorsa, veritabanındaki eski kaydı çekip eski user'ı alırız
            old_instance = UserSite.objects.get(pk=instance.pk)
            old_user = old_instance.user
    except ObjectDoesNotExist:
        pass

    new_user = instance.user

    # (A) Eski kullanıcıdan yeni kullanıcıya devir yapılıyorsa
    if old_user and (old_user != new_user):
        # Eski kullanıcıda (old_user) başka site kalmadıysa -> pasif yap
        old_user_sites = old_user.userSites.exclude(pk=instance.pk)
        if not old_user_sites.exists():
            old_user.is_active = False
            old_user.selectedSite = None
            old_user.save()

    # (B) Yeni kullanıcı -> Aktif yap, selectedSite güncelle
    if not new_user.is_active:
        new_user.is_active = True
    new_user.selectedSite = instance.site
    new_user.save()


@receiver(post_save, sender=UserSite)
def update_selected_site_on_creation(sender, instance, created, **kwargs):
    """
    Bir UserSite kaydı oluşturulduğunda (created=True),
    ilgili kullanıcının selectedSite alanını ve aktifliğini günceller.

    * Yalnızca yeni kayıt ekleme durumunda (created=True) tetiklenir.
    * Güncelleme yapıldığında created=False olur; bu fonksiyon "yeni ekleme" mantığı çalıştırmaz.
    """
    if created:
        user = instance.user
        user.selectedSite = instance.site

        # Kullanıcı pasifse, aktif hale getir
        if not user.is_active:
            user.is_active = True

        user.save()


@receiver(post_delete, sender=UserSite)
def handle_user_site_deletion(sender, instance, **kwargs):
    """
    Bir UserSite kaydı silindiğinde (admin panelinden veya kod ile),
    eğer kullanıcının başka site ilişkisi kalmadıysa pasif yap ve selectedSite=None.
    Kalan site varsa en güncel siteyi 'selectedSite' yapıp aktif tut.

    Örnek:
      - Kullanıcıya ait tek UserSite kaydı silindiyse, kullanıcı pasif yapılır (is_active=False).
      - Kullanıcının başka site ilişkisi varsa, o sitelerden en günceline geçilir.
    """
    user = instance.user
    remaining_sites = user.userSites.all()

    if remaining_sites.exists():
        # En az bir site kaldıysa, en güncel site ile devam et
        latest_user_site = remaining_sites.order_by('-createdAt').first()
        user.selectedSite = latest_user_site.site
        user.is_active = True
        user.save()
    else:
        # Hiç site kalmadıysa pasif yap
        user.selectedSite = None
        user.is_active = False
        user.save()
