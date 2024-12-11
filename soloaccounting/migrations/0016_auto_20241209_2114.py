from django.db import migrations
from django.utils.text import slugify

def populate_slug(apps, schema_editor):
    Product = apps.get_model('soloaccounting', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            product.slug = slugify(product.name)
            product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('soloaccounting', '0015_product_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slug),
    ]
