# Generated by Django 4.0.3 on 2022-06-07 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escalada', '0010_alter_coupon_classtype_alter_coupon_climbpasstype'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Enrollment',
            new_name='Lesson',
        ),
    ]