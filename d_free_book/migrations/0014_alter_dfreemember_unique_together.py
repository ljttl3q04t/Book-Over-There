# Generated by Django 4.2.3 on 2023-07-25 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0034_category_follower'),
        ('d_free_book', '0013_remove_dfreeorderdetail_book_note_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dfreemember',
            unique_together={('club', 'code'), ('club', 'phone_number')},
        ),
    ]
