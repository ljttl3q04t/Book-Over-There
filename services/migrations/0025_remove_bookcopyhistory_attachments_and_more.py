# Generated by Django 4.2.2 on 2023-06-28 09:51

from django.db import migrations, models
import services.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0024_alter_bookcopyhistory_action_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookcopyhistory',
            name='attachments',
        ),
        migrations.AddField(
            model_name='bookcopyhistory',
            name='attachment',
            field=models.FileField(null=True, storage=services.storage_backends.BookHistoryStorage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='bookcopyhistory',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]