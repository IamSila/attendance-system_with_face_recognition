from django.db import models
from django.utils import timezone
# Create your models here.
# calender tasks
class Task(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField() 
    location = models.CharField(max_length=256)
    courseCode = models.CharField(max_length=5, default='j17')

    def __str__(self):
        return self.title



# Register and Students model
class StudentProfile(models.Model):
    # Required fields
    first_name = models.CharField(max_length=256)  # null=False is default for CharField
    last_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256, unique=True)
    course = models.CharField(max_length=200)
    phone = models.BigIntegerField(unique=True)
    email = models.EmailField(unique=False)
    password = models.CharField(max_length=256)
    
    # Optional fields - corrected middle_name field
    middle_name = models.CharField(
        max_length=256, 
        blank=True,  # Allows empty string in forms
        null=True,    # Allows NULL in database
        default=''    # Default value when not provided
    )
    
    ranking = models.CharField(max_length=256, blank=True, default='')
    image = models.ImageField(upload_to='student_photos', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name} ({self.username})"


# Model to store attendance records
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], default='absent')
    
    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.class_name} - {self.date}"