# Generated by Django 5.1.3 on 2024-12-03 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soloblog', '0003_remove_category_unique_order_per_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='homepage',
        ),
        migrations.AddField(
            model_name='article',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='Öne Çıkan'),
        ),
    ]
