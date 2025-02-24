# Generated by Django 5.1.3 on 2024-12-20 23:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('common', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
        ('soloaccounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='dealer_segment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='soloaccounting.dealersegment', verbose_name='Bayi Segmenti'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='CustomUser_groups', to='auth.group', verbose_name='Gruplar'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='selectedSite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sites.site', verbose_name='Aktif Seçilen Site'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='CustomUser_permissions', to='auth.permission', verbose_name='Kullanıcı İzinleri'),
        ),
        migrations.AddField(
            model_name='googleapplicationsintegration',
            name='site',
            field=models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site'),
        ),
        migrations.AddField(
            model_name='logentry',
            name='site',
            field=models.ForeignKey(help_text='Logun ait olduğu site', on_delete=django.db.models.deletion.CASCADE, related_name='log_entries', to='sites.site'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='site',
            field=models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site'),
        ),
        migrations.AddField(
            model_name='smssettings',
            name='site',
            field=models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site'),
        ),
        migrations.AddField(
            model_name='smtpsettings',
            name='site',
            field=models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site'),
        ),
        migrations.AddField(
            model_name='whatsappsettings',
            name='site',
            field=models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site'),
        ),
    ]
