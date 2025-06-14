# Generated by Django 5.2.1 on 2025-05-23 11:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_alter_ad_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='title',
            field=models.CharField(max_length=50, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='exchangeproposal',
            name='comment',
            field=models.TextField(blank=True, validators=[django.core.validators.MaxLengthValidator(500)], verbose_name='комментарий'),
        ),
    ]
