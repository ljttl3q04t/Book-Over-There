# Generated by Django 4.2.3 on 2023-07-31 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0038_alter_user_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
