# Generated by Django 5.0.8 on 2024-12-06 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0002_profile_referral_code_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='referral_code',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
