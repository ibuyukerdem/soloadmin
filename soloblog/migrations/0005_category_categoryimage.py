# Generated by Django 5.1.3 on 2024-12-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soloblog', '0004_remove_article_homepage_article_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='categoryImage',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/', verbose_name='Kategori Görseli'),
        ),
    ]
