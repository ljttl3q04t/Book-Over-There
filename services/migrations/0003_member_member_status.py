# Generated by Django 4.2.2 on 2023-06-14 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_bookclub_member_membership_member_book_clubs_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_status',
            field=models.CharField(choices=[('active', 'Active'), ('banned', 'Banned')], default='active', max_length=10),
        ),
    ]
