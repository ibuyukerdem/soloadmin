# Generated by Django 5.1.3 on 2024-12-03 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('soloblog', '0002_category_unique_order_per_site'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='category',
            name='unique_order_per_site',
        ),
    ]
