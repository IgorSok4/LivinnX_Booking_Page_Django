# Generated by Django 3.2.16 on 2023-05-10 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AmenityBooker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationmodel',
            name='hours_booked',
            field=models.ManyToManyField(null=True, related_name='hours_booked', to='AmenityBooker.Hour'),
        ),
    ]
