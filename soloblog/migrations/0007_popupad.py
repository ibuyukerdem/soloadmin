# Generated by Django 5.1.3 on 2024-12-03 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('soloblog', '0006_article_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopupAd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='HTML veya metin içerik.', verbose_name='Reklam İçeriği')),
                ('isActive', models.BooleanField(default=True, help_text='Reklam aktif mi?', verbose_name='Aktif')),
                ('createdAt', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
                ('sites', models.ManyToManyField(help_text='Bu reklamın gösterileceği siteler.', related_name='popup_ads', to='sites.site', verbose_name='Bağlı Siteler')),
            ],
            options={
                'verbose_name': 'Pop-up Reklam',
                'verbose_name_plural': 'Pop-up Reklamları',
                'ordering': ['-createdAt'],
            },
        ),
    ]
