# Generated by Django 5.1.3 on 2024-12-04 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_whatsappsettings_kontormiktari'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='smssettings',
            options={'verbose_name': 'SMS Ayarı', 'verbose_name_plural': 'A-SMS Ayarları'},
        ),
        migrations.AlterModelOptions(
            name='smtpsettings',
            options={'verbose_name': 'SMTP Ayarı', 'verbose_name_plural': 'A-SMTP Ayarları'},
        ),
        migrations.AlterModelOptions(
            name='whatsappsettings',
            options={'verbose_name': 'WhatsApp Ayarı', 'verbose_name_plural': 'A-WhatsApp Ayarları'},
        ),
    ]
