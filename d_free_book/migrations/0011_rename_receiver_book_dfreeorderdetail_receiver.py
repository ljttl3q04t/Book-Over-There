# Generated by Django 4.2.3 on 2023-07-20 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('d_free_book', '0010_dfreeorder_creator_order_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dfreeorderdetail',
            old_name='receiver_book',
            new_name='receiver',
        ),
    ]