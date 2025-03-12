from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.

#The home page view
def Home(request):
    return render(request, 'home.html')


# register page view
def Register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        user_data_has_error = False

        # checking if student exists.
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Student already exists!")
        # checking if email exists
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "email already exists!")
        if len(password) < 8:
            user_data_has_error = True
            messages.error(request, "Password is too short")
        if password != confirmPassword:
            user_data_has_error = True
            messages.error(request, "Passwords do not match!")
        
        if user_data_has_error:
            return redirect('register')
        else:
            newUser = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            messages.success(request, "Account created successfully, login now")

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
        })
    return JsonResponse(tasks_list, safe=False)

def Planning(request):
    return render(request, 'planning2.html')


def Dashboard(request):
    return render(request, 'dashboard.html')