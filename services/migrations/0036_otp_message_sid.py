# Generated by Django 4.2.3 on 2023-07-31 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0035_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='message_sid',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
