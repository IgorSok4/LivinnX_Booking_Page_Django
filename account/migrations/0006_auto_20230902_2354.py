# Generated by Django 3.2.16 on 2023-09-02 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20230902_2353'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='blue_conference_room_active',
            new_name='blue_active',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='orange_conference_room_active',
            new_name='orange_active',
        ),
    ]