# Generated by Django 5.1.6 on 2025-03-08 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_razorpaypayment_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='OTP',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='otp_create',
            field=models.DateTimeField(auto_now_add=True, default='2025-02-26 05:44:55'),
            preserve_default=False,
        ),
    ]
