# Generated by Django 5.1.3 on 2024-12-20 23:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='SitePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='İzin kodu: örn solosite.view_apartment', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, help_text='Oluşturulma tarihi')),
                ('updatedAt', models.DateTimeField(auto_now=True, help_text='Son güncelleme tarihi')),
                ('name', models.CharField(help_text='Rol adı: admin, manager, staff', max_length=50)),
                ('code', models.CharField(help_text='Rol kodu: admin, manager, staff', max_length=50, unique=True)),
                ('site', models.ForeignKey(help_text='Bu kaydın ait olduğu siteyi belirtir.', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='sites.site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteRolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rolePermissions', to='solosite.sitepermission')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rolePermissions', to='solosite.siterole')),
            ],
            options={
                'unique_together': {('role', 'permission')},
            },
        ),
        migrations.CreateModel(
            name='SiteUserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignedUsers', to='solosite.siterole')),
                ('userProfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='siteUserRoles', to='accounts.userprofile')),
            ],
            options={
                'unique_together': {('userProfile', 'role')},
            },
        ),
    ]
