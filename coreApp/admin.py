from django.contrib import admin
from .models import Task, Student, Profile
# Register your models here.
admin.site.register(Task)
admin.site.register(Student)
admin.site.register(Profile)