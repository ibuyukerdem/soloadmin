# Generated by Django 5.1.3 on 2024-12-03 10:44

import django.db.models.deletion
import soloblog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('categoryName', models.CharField(max_length=255, verbose_name='Kategori Adı')),
                ('categoryDescription', models.TextField(verbose_name='Kategori Açıklaması')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='URL Yolu')),
                ('meta', models.TextField(blank=True, null=True, verbose_name='Meta Veriler')),
                ('metaDescription', models.TextField(blank=True, null=True, verbose_name='Meta Açıklaması')),
                ('order', models.IntegerField(default=0, verbose_name='Sıra')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='soloblog.category', verbose_name='Üst Kategori')),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
            ],
            options={
                'verbose_name': 'Kategori',
                'verbose_name_plural': 'Kategoriler',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('title', models.CharField(max_length=255, verbose_name='Başlık')),
                ('content', models.TextField(verbose_name='İçerik')),
                ('homepage', models.BooleanField(default=False, verbose_name='Anasayfa Gösterimi')),
                ('slider', models.BooleanField(default=False, verbose_name='Slider Gösterimi')),
                ('active', models.BooleanField(default=True, verbose_name='Aktif')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='URL Yolu')),
                ('counter', models.IntegerField(default=0, verbose_name='Sayaç')),
                ('meta', models.TextField(blank=True, null=True, verbose_name='Meta Veriler')),
                ('metaDescription', models.TextField(blank=True, null=True, verbose_name='Meta Açıklaması')),
                ('publicationDate', models.DateTimeField(auto_now_add=True, verbose_name='Yayınlanma Tarihi')),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soloblog.category', verbose_name='Kategori')),
            ],
            options={
                'verbose_name': 'Makale',
                'verbose_name_plural': 'Makaleler',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('approved', models.BooleanField(default=False, verbose_name='Onay Durumu')),
                ('firstName', models.CharField(max_length=255, verbose_name='Ad')),
                ('lastName', models.CharField(max_length=255, verbose_name='Soyad')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('phoneNumber', models.CharField(max_length=15, verbose_name='Telefon Numarası')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1, verbose_name='Yıldız Puanı')),
                ('content', models.TextField(verbose_name='Yorum')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='soloblog.article', verbose_name='Makale')),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
            ],
            options={
                'verbose_name': 'Yorum',
                'verbose_name_plural': 'Yorumlar',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('imagePath', models.ImageField(upload_to=soloblog.models.get_image_upload_path, verbose_name='Resim Yolu')),
                ('resizedImage', models.ImageField(blank=True, null=True, upload_to=soloblog.models.get_image_upload_path, verbose_name='Boyutlandırılmış Resim')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='soloblog.article', verbose_name='Makale')),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
            ],
            options={
                'verbose_name': 'Makale Resim',
                'verbose_name_plural': 'Makale Resimleri',
            },
        ),
    ]
