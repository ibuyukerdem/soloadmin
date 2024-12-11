# Generated by Django 5.1.3 on 2024-12-04 10:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_smssettings'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('apiUrl', models.URLField(max_length=500, verbose_name='WhatsApp API URL')),
                ('phoneNumber', models.CharField(max_length=20, verbose_name='Telefon Numarası')),
                ('apiKey', models.CharField(max_length=255, verbose_name='API Anahtarı')),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
            ],
            options={
                'verbose_name': 'WhatsApp Ayarı',
                'verbose_name_plural': 'WhatsApp Ayarları',
                'db_table': 'whatsapp_settings',
            },
        ),
    ]