# Generated by Django 5.1.7 on 2025-03-31 17:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0003_alter_account_updated_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='reporting_code',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='account',
            name='updated_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 31, 22, 51, 39, 438370)),
        ),
    ]
