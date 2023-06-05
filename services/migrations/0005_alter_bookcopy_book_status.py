# Generated by Django 4.2.1 on 2023-06-05 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_order_orderdetail_wishlist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcopy',
            name='book_status',
            field=models.CharField(choices=[('new', 'New'), ('used', 'Used'), ('lost', 'Lost'), ('return', 'Return'), ('borrowed', 'Borrowed')], default='new', max_length=20),
        ),
    ]
