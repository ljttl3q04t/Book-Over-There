# Generated by Django 4.2.3 on 2023-07-25 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('d_free_book', '0015_dfreedraff_remove_dfreeorder_address'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DFreeDraff',
            new_name='DFreeDraffOrder',
        ),
        migrations.RenameField(
            model_name='dfreedrafforder',
            old_name='club_book',
            new_name='club_books',
        ),
    ]
