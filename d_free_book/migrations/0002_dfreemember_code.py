# Generated by Django 4.2.2 on 2023-07-12 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('d_free_book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dfreemember',
            name='code',
            field=models.CharField(default=None, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]