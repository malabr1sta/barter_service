# Generated by Django 5.2.1 on 2025-05-23 11:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_alter_ad_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='description',
            field=models.TextField(validators=[django.core.validators.MaxLengthValidator(500)], verbose_name='описание'),
        ),
    ]
