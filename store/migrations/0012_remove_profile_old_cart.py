# Generated by Django 4.2.16 on 2024-12-10 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_profile_old_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='old_cart',
        ),
    ]
