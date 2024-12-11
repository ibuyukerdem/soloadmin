# Generated by Django 5.1.3 on 2024-12-07 11:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soloaccounting', '0011_remove_siteurun_updatedate_remove_siteurun_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='createdAt',
        ),
        migrations.RemoveField(
            model_name='product',
            name='site',
        ),
        migrations.RemoveField(
            model_name='product',
            name='updatedAt',
        ),
        migrations.AddField(
            model_name='product',
            name='createDate',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 1, 0, 0), help_text='Bu kaydın oluşturulma tarihi.', verbose_name='Oluşturulma Tarihi'),
        ),
        migrations.AddField(
            model_name='product',
            name='updateDate',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 1, 0, 0), help_text='Bu kaydın son güncellenme tarihi.', verbose_name='Güncellenme Tarihi'),
        ),
    ]
