# Generated by Django 4.2.2 on 2023-06-19 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_remove_memberbookcopy_book_memberbookcopy_book_copy_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcopy',
            name='book_deposit_price',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='bookcopy',
            name='book_deposit_status',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
