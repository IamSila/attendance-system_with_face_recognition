from django.shortcuts import render, get_object_or_404, redirect
from .models import Task, StudentProfile, Attendance
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import os

# Create your views here.

#The home page view
def Home(request):
    return render(request, 'home.html')

def Base(request):
    return render(request, 'base.html')


# register page view
def Register(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        course = request.POST.get('course')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        ranking = request.POST.get('ranking')
        image = request.FILES.get('image')

        user_data_has_error = False

        # Validation checks
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists!")
        
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists!")
        
        if len(password) < 8:
            user_data_has_error = True
            messages.error(request, "Password is too short")
        
        if password != confirmPassword:
            user_data_has_error = True
            messages.error(request, "Passwords do not match!")
        
        if not image:
            user_data_has_error = True
            messages.error(request, "Please upload a profile image")
        
        if user_data_has_error:
            return redirect('register')
        
        try:
            # Create User object
            newUser = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )

            # Create StudentProfile object
            StudentProfile.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                username=username,
                course=course,
                phone=phone,
                email=email,
                password=password,
                ranking=ranking,
                image=image
            )

            messages.success(request, "Account created successfully, login now")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('register')

    return render(request, 'register.html')


# login view
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('login')
    return render(request, 'login.html')

# logout view
def Logout(request):
    logout(request)
    return redirect('home')

# Calender / planning
@login_required
def get_tasks(request):
    tasks = Task.objects.all()
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'start': task.start_time.isoformat(),
            'end': task.end_time.isoformat(),
            'courseCode': task.courseCode,
        })
    return JsonResponse(tasks_list, safe=False)
@login_required
def Planning(request):
    return render(request, 'planning2.html')

@login_required
def Dashboard(request):
    tasks = Task.objects.all()
    context = {'tasks':tasks}
    return render(request, 'dashboard.html', context)

@login_required
def Profile(request):
    return render(request, 'profile.html')

@login_required
def UpdateProfile(request):
    return render(request, 'profileUpdate.html')


@login_required
def MarkAttendance(request):
   return render(request, 'markAttendance.html')