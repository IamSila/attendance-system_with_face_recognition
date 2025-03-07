from django.db import models

# Create your models here.
# calender tasks
class Task(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.title