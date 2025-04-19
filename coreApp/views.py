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
            student_profile = StudentProfile.objects.create(
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

            # Save the profile image to student_photos directory
            student_photos_dir = 'media/student_photos'
            if not os.path.exists(student_photos_dir):
                os.makedirs(student_photos_dir)
            
            # Save the image with username as filename
            file_extension = os.path.splitext(image.name)[1]
            student_photo_path = os.path.join(student_photos_dir, f"{username}{file_extension}")
            with open(student_photo_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

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
def MarkAttendance(request, class_name=None):
    if request.method == 'POST':
        try:
            # Get the recognized profile ID from session
            profile_id = request.session.get('recognized_profile_id')
            if not profile_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No recognized profile found!'
                })

            # Get the class name from either URL pattern or GET parameters
            class_name = class_name or request.GET.get('class_name')
            if not class_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No class name provided!'
                })

            # Get the current date and time
            current_date = datetime.now().date()
            current_time = datetime.now().time()

            # Check if attendance already exists for today
            existing_attendance = Attendance.objects.filter(
                student_id=profile_id,
                class_name=class_name,
                date=current_date
            ).first()

            if existing_attendance:
                return JsonResponse({
                    'status': 'warning',
                    'message': 'Attendance already marked for this class today!'
                })

            # Create new attendance record
            Attendance.objects.create(
                student_id=profile_id,
                class_name=class_name,
                date=current_date,
                time=current_time,
                status='present'
            )

            # Clear the session
            if 'recognized_profile_id' in request.session:
                del request.session['recognized_profile_id']

            return JsonResponse({
                'status': 'success',
                'message': 'Attendance marked successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error marking attendance: {str(e)}'
            })

    # For GET requests, render the template with class name
    context = {'class_name': class_name} if class_name else {}
    return render(request, 'markAttendance.html', context)

@login_required
def recognize_face(request):
    try:
        # Get the uploaded image
        uploaded_image = request.FILES.get('captured_image')
        if not uploaded_image:
            return JsonResponse({
                'status': 'error',
                'message': 'No image captured!'
            })

        # Save the uploaded image temporarily
        temp_path = 'media/temp_captured.jpg'
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        # Get all student photos from the directory
        student_photos_dir = 'media/student_photos'
        if not os.path.exists(student_photos_dir):
            os.makedirs(student_photos_dir)
            return JsonResponse({
                'status': 'error',
                'message': 'Student photos directory created. Please add student photos to the directory.'
            })

        # Load the captured image
        captured_image = face_recognition.load_image_file(temp_path)
        captured_face_encodings = face_recognition.face_encodings(captured_image)

        if not captured_face_encodings:
            return JsonResponse({
                'status': 'error',
                'message': 'No face detected in captured image!'
            })

        # Load all student photos and their encodings at once
        student_encodings = []
        student_usernames = []
        
        for filename in os.listdir(student_photos_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                student_photo_path = os.path.join(student_photos_dir, filename)
                student_image = face_recognition.load_image_file(student_photo_path)
                student_face_encodings = face_recognition.face_encodings(student_image)
                
                if student_face_encodings:
                    student_encodings.append(student_face_encodings[0])
                    student_usernames.append(filename.split('.')[0])

        if not student_encodings:
            return JsonResponse({
                'status': 'error',
                'message': 'No student photos found in the directory. Please add student photos.'
            })

        # Compare the captured face with all student faces at once
        matches = face_recognition.compare_faces(student_encodings, captured_face_encodings[0])
        
        if True in matches:
            matched_index = matches.index(True)
            matched_student = student_usernames[matched_index]
            
            try:
                student_profile = StudentProfile.objects.get(username=matched_student)
                # Store the recognized profile in session for attendance marking
                request.session['recognized_profile_id'] = student_profile.id
                
                # Clean up temporary file
                os.remove(temp_path)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Face recognized! Marking attendance...',
                    'student_id': matched_student
                })
            except StudentProfile.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student profile not found!'
                })
        else:
            # Clean up temporary file
            os.remove(temp_path)
            return JsonResponse({
                'status': 'error',
                'message': 'Face not recognized. Please try again!'
            })

    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        })


def customAdmin(request):
    return render(request, 'admin/adminBase.html')

def studentRecords(request):
    return render(request, 'admin/studentRecords.html')

def createRecords(request):
    return render(request, 'admin/createRecords.html')