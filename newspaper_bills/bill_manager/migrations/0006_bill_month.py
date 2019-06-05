# Generated by Django 2.2.1 on 2019-06-03 12:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill_manager', '0005_remove_bill_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='month',
            field=models.IntegerField(default=62019, validators=[django.core.validators.MinValueValidator(12000), django.core.validators.MaxValueValidator(129999)]),
            preserve_default=False,
        ),
    ]
