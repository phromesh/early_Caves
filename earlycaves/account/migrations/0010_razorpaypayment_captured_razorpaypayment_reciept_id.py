# Generated by Django 5.1.6 on 2025-03-05 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_razorpaypayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='razorpaypayment',
            name='captured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='razorpaypayment',
            name='reciept_id',
            field=models.CharField(default='EARLY_20250305123045_a1b2c3', max_length=30, unique=True),
            preserve_default=False,
        ),
    ]
