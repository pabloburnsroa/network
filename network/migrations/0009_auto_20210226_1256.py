# Generated by Django 3.1.5 on 2021-02-26 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_auto_20210226_1121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='liked',
            new_name='likes',
        ),
    ]
