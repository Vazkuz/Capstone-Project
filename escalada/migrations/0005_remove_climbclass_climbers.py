# Generated by Django 4.0.3 on 2022-06-01 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escalada', '0004_climbclass_starthour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='climbclass',
            name='climbers',
        ),
    ]
