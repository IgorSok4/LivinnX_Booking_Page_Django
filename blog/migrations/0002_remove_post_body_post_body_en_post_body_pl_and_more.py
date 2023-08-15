# Generated by Django 4.1.5 on 2023-08-05 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='body',
        ),
        migrations.AddField(
            model_name='post',
            name='body_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='body_pl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='body_ru',
            field=models.TextField(null=True),
        ),
    ]
