from django.shortcuts import render, get_object_or_404, redirect
from .models import Task, StudentProfile, Attendance
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Case, When, IntegerField
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import os
from django.http import JsonResponse

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
            'location' : task.location,
        })
    return JsonResponse(tasks_list, safe=False)
@login_required
def Planning(request):
    return render(request, 'planning3.html')

@login_required
def Dashboard(request):
    tasks = Task.objects.all()
    context = {'tasks':tasks}
    return render(request, 'dashboard.html', context)

@login_required
def Profile(request, username):
    student = get_object_or_404(StudentProfile, username=username)
    context = {}
    context['student'] = student
    return render(request, 'profile.html', context)

@login_required
def UpdateProfile(request, username):
    student = get_object_or_404(StudentProfile, username=username)
    context = {'student': student}

    if request.method == "POST":
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        if (not student.email):
            messages.error(request, "email must be provided")
        elif (not student.phone):
            messages.error(request, "Phone cannot be empty")
        else:
            student.save()
    return render(request, 'profileUpdate.html', context)


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

            # Get the class name
            class_name = class_name or request.GET.get('class_name')
            if not class_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No class name provided!'
                })

            # Get current student
            current_student = StudentProfile.objects.get(id=profile_id)
            username_prefix = current_student.username.split('-')[0]

            # Get all students with matching username prefix
            matching_students = StudentProfile.objects.filter(
                username__startswith=username_prefix + '-'
            )

            current_date = datetime.now().date()
            current_time = datetime.now().time()

            # Create attendance records for all matching students (default: absent)
            for student in matching_students:
                Attendance.objects.get_or_create(
                    student=student,
                    class_name=class_name,
                    date=current_date,
                    defaults={
                        'status': 'absent',
                        'time': None
                    }
                )

            # Mark current student as present
            Attendance.objects.update_or_create(
                student_id=profile_id,
                class_name=class_name,
                date=current_date,
                defaults={
                    'status': 'present',
                    'time': current_time
                }
            )

            # Clear the session
            if 'recognized_profile_id' in request.session:
                del request.session['recognized_profile_id']

            return JsonResponse({
                'status': 'success',
                'message': 'Attendance marked successfully!'
            })

        except StudentProfile.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Student profile not found!'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error marking attendance: {str(e)}'
            })

    # For GET requests, render the template with class name
    context = {
        'class_name': class_name if class_name else None
    }
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

def myAttendance(request, username):
    # Get the student object or return 404 if not found
    student = get_object_or_404(StudentProfile, username=username)


    # Filter attendance records for this student only
    attendance_records = Attendance.objects.filter(
        student=student
    ).order_by('-date', '-time')  # Newest records first
    
      # Get counts of present and absent records
    attendance_stats = attendance_records.aggregate(
        total_present=Count(
            Case(
                When(status='present', then=1),
                output_field=IntegerField()
            )
        ),
        total_absent=Count(
            Case(
                When(status='absent', then=1),
                output_field=IntegerField()
            )
        ),
        # total_records=Count('id')  # Total records (optional)
    )
    # getting all total records
    total_records = attendance_records.count()
    attendance_percentage = ((attendance_stats['total_present'] + attendance_stats['total_absent']) / total_records) * 100
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_present': attendance_stats['total_present'],
        'total_absent': attendance_stats['total_absent'],
        'total_records': total_records,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'myAttendance.html', context)



# admin section

def customAdmin(request):
    return render(request, 'admin/adminBase.html')

def studentRecords(request):
    context = {}
    students = StudentProfile.objects.all()
    context['students'] = students
    return render(request, 'admin/studentRecords.html', context)

def createStudent(request):
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
        ranking = request.POST.get('ranking')
        image = request.FILES.get('image')

        user_data_has_error = False

        # Validation checks
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Reg Number already exists!")
        
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists!")
        
        if len(password) < 8:
            user_data_has_error = True
            messages.error(request, "Password is too short")
        
        # if not image:
        #     user_data_has_error = True
        #     messages.error(request, "Please upload a profile image")
        
        if user_data_has_error:
            return redirect('createStudent')
        
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

            messages.success(request, "Student profile created successfully!")
            return redirect('createStudent')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('createStudent')

    return render(request, 'admin/createStudent.html')

def createTask(request):
    # Task Creation
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        courseCode = request.POST.get('courseCode')
        location = request.POST.get('location')

        try:
            new_task = Task(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                courseCode=courseCode,
                location=location,
            )
            new_task.save()
            messages.success(request, "Task Added Successfully")
        except Exception as e:
            messages.error(request, f"Error saving task: {str(e)}")

        return redirect('createTask')

    return render(request, 'admin/createTask.html') 

def attendanceRecords(request):
    records = Attendance.objects.all()
    context = {}
    context['records'] = records
    return render(request, 'admin/attendanceRecords.html', context)

def update(request, username):
    updateStudent = get_object_or_404(StudentProfile, username=username)
    context = {}

    if request.method == 'POST':
        updateStudent.first_name=request.POST.get('first_name')
        updateStudent.middle_name=request.POST.get('middle_name')
        updateStudent.last_name=request.POST.get('last_name')
        updateStudent.username=request.POST.get('username')
        updateStudent.course=request.POST.get('course')
        updateStudent.phone=request.POST.get('phone')
        updateStudent.email=request.POST.get('email')
        updateStudent.password=request.POST.get('password')
        updateStudent.ranking=request.POST.get('ranking')
        # new_profile_photo = request.FILES.get('image')  # Use FILES for image uploads

        # if new_profile_photo:
        #     # If a new image is uploaded, update the field
        #     updateStudent.image = new_profile_photo
        # else:
        #     # If no new image is provided, keep the existing image
        #     # This line isn't necessary unless you overwrite the field elsewhere
        #     pass
        updateStudent.save()

    context['updateStudent'] = updateStudent
    return render(request, 'admin/updateStudent.html', context)

def delete(request, username):
    student_to_delete = get_object_or_404(StudentProfile, username=username)
    if request.method == 'POST':
        confirmation_username = request.POST.get('confirmation_username')
        if (confirmation_username == username):
            deleteStudent = get_object_or_404(StudentProfile, username=confirmation_username)
            deleteStudent.delete()
            messages.success(request, f"Student {student_to_delete} has been successfully deleted!")
            return redirect('studentRecords')
        else:
            messages.error(request, f"Student deletion for {student_to_delete} failed. Please enter the exact username to confirm deletion!")
            # return redirect('deletePage')
            
        # except Exception as e:
        #     messages.error(request, f"Error deleting student: {str(e)}")

    # If GET request, show confirmation page
    student = get_object_or_404(StudentProfile, username=username)
    return render(request, 'admin/delete.html', {'student': student})

def deleteView(request):
    return render(request, 'admin/delete.html')
