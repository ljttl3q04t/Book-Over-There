# Generated by Django 4.2.2 on 2023-06-26 14:31

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('services', '0020_remove_member_member_status_membership_member_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='memberbookcopy',
            name='book_status',
        ),
    ]
