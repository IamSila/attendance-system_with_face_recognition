# Generated by Django 5.1.6 on 2025-03-31 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0008_attendance_studentprofile_delete_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='ranking',
            field=models.CharField(max_length=256),
        ),
    ]
