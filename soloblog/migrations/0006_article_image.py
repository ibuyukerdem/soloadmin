# Generated by Django 5.1.3 on 2024-12-03 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soloblog', '0005_category_categoryimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='article_images/', verbose_name='Makale Resmi'),
        ),
    ]
