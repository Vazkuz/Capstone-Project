# Generated by Django 4.0.3 on 2022-06-28 21:24

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('escalada', '0028_alter_weekdayschedule_weekday'),
    ]

    operations = [
        UnaccentExtension()
    ]