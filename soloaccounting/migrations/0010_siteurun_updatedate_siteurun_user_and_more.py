# Generated by Django 5.1.3 on 2024-12-07 09:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('soloaccounting', '0009_alter_siteurun_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteurun',
            name='updateDate',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi'),
        ),
        migrations.AddField(
            model_name='siteurun',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='siteUrun', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı'),
        ),
        migrations.AlterField(
            model_name='siteurun',
            name='site',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='urunSite', to='sites.site', verbose_name='Site'),
        ),
    ]
