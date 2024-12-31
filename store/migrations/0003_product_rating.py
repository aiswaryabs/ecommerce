# Generated by Django 4.2.16 on 2024-11-28 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_is_sale_product_sale_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, help_text='Product rating out of 5.0', max_digits=3),
        ),
    ]
