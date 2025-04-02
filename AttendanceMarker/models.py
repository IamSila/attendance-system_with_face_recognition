# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_encoding = models.TextField()  # Stores facial features as string
    employee_id = models.CharField(max_length=50, unique=True)
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.FloatField()  # Latitude of check-in
    location_long = models.FloatField()  # Longitude of check-in
    verified = models.BooleanField(default=False)  # Whether location and face matched
    image = models.ImageField(upload_to='attendance_images/')  # Store captured image