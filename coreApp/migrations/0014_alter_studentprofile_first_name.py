# Generated by Django 4.2.20 on 2025-04-21 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0013_alter_studentprofile_middle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='first_name',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
