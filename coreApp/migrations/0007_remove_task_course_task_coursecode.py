# Generated by Django 4.2.20 on 2025-03-28 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0006_alter_task_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='course',
        ),
        migrations.AddField(
            model_name='task',
            name='courseCode',
            field=models.CharField(default='j17', max_length=5),
        ),
    ]
