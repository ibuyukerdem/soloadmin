# Generated by Django 5.1.3 on 2024-12-22 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='isIndividual',
            field=models.BooleanField(default=False, verbose_name='Kurumsal Fatura İstiyorum'),
        ),
    ]
