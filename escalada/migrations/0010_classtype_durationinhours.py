# Generated by Django 4.0.3 on 2022-06-02 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalada', '0009_remove_climbclass_starthour_climbclass_begin_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='classtype',
            name='durationInHours',
            field=models.IntegerField(default=2),
        ),
    ]
