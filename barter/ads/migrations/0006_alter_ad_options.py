# Generated by Django 5.2.1 on 2025-05-24 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0005_alter_ad_options_alter_exchangeproposal_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ad',
            options={'ordering': ['-created_at', '-updated_at'], 'verbose_name': 'Объявление', 'verbose_name_plural': 'Объявления'},
        ),
    ]
