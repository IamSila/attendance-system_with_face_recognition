from django.contrib import admin
from .models import Task, StudentProfile, Attendance
# Register your models here.
admin.site.register(Task)
admin.site.register(StudentProfile)
admin.site.register(Attendance)
