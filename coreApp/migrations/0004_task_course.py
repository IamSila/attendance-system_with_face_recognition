# Generated by Django 4.2.20 on 2025-03-28 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0003_alter_task_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='course',
            field=models.CharField(default='comp sci', max_length=256),
        ),
    ]
