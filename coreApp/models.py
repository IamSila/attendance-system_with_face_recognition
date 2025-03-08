from django.db import models
from django.utils import timezone
# Create your models here.
# calender tasks
class Task(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField() 

    def __str__(self):
        return self.title



# Register and Students model
class Student(models.Model):
    first_name = models.CharField(max_length=256)
    middle_name = models.CharField(max_length=256, default="jane")
    last_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    email = models.EmailField()
    password = models.CharField(max_length=256)
    
    def __str__(self):
        return f"{self.firstName} {self.lastName} {self.username}"


