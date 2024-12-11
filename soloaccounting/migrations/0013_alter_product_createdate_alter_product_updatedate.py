# Generated by Django 5.1.3 on 2024-12-07 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soloaccounting', '0012_remove_product_createdat_remove_product_site_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='createDate',
            field=models.DateTimeField(auto_now_add=True, help_text='Bu kaydın oluşturulma tarihi otomatik olarak ayarlanır.', verbose_name='Oluşturulma Tarihi'),
        ),
        migrations.AlterField(
            model_name='product',
            name='updateDate',
            field=models.DateTimeField(auto_now=True, help_text='Bu kaydın son güncellenme tarihi otomatik olarak ayarlanır.', verbose_name='Güncellenme Tarihi'),
        ),
    ]