# Generated by Django 5.1.3 on 2024-12-04 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('soloblog', '0009_visitoranalytics'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='visitoranalytics',
            index=models.Index(fields=['site'], name='soloblog_vi_site_id_038723_idx'),
        ),
        migrations.AddIndex(
            model_name='visitoranalytics',
            index=models.Index(fields=['article'], name='soloblog_vi_article_c1ef94_idx'),
        ),
        migrations.AddIndex(
            model_name='visitoranalytics',
            index=models.Index(fields=['visit_date'], name='soloblog_vi_visit_d_4bd6bb_idx'),
        ),
    ]