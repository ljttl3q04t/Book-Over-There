# Generated by Django 4.2.3 on 2023-07-19 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0035_merge_20230719_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookcopy',
            name='book_image',
        ),
    ]
