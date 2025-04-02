from django.db import models
from django.utils import timezone
# Create your models here.
# calender tasks
class Task(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField() 
    location = models.CharField(max_length=256)
    courseCode = models.CharField(max_length=5, default='j17')

    def __str__(self):
        return self.title



# Register and Students model
class StudentProfile(models.Model):
    first_name = models.CharField(max_length=256)
    middle_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    course = models.CharField(max_length=200)
    phone = models.BigIntegerField()
    email = models.EmailField()
    password = models.CharField(max_length=256)
    ranking = models.CharField(max_length=256)
    image = models.ImageField(upload_to='student_photos')


    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.username}"


# Model to store attendance records
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ])
    
    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.class_name} - {self.date}"