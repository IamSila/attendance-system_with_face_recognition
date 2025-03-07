from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.

#The home page view
def Home(request):
    return render(request, 'home.html')

# login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            redirect('')
        else:
            messages.error(request, "Invalid Username or Password")
            redirect('login')
    return render(request, 'login.html')

# Calender / planning
def Planning(request):
    tasks = Task.objects.all()
    context = {"tasks": tasks}
    return render(request, 'planning.html', context)