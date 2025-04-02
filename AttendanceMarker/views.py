from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Employee, Attendance
from .services import FaceRecognitionService, LocationService
import json


# Define your allowed locations (office coordinates)
ALLOWED_LOCATIONS = {
    'main_office': {'lat': 12.9716, 'long': 77.5946},  # Example: Bangalore coordinates
}

@csrf_exempt
@login_required
def register_face(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            # Get face encoding
            face_encoding = FaceRecognitionService.get_face_encoding(image_data)
            if not face_encoding:
                return JsonResponse({'success': False, 'error': 'No face detected'})
                
            # Save to employee profile
            employee, created = Employee.objects.get_or_create(user=request.user)
            employee.face_encoding = face_encoding
            employee.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def mark_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            user_lat = data.get('latitude')
            user_long = data.get('longitude')
            
            # Verify location
            location_verified = False
            for location_name, coords in ALLOWED_LOCATIONS.items():
                if LocationService.is_within_radius(
                    user_lat, user_long, 
                    coords['lat'], coords['long']
                ):
                    location_verified = True
                    break
                    
            if not location_verified:
                return JsonResponse({
                    'success': False, 
                    'error': 'You must be at an authorized location to mark attendance'
                })
            
            # Verify face
            employee = Employee.objects.get(user=request.user)
            face_verified = FaceRecognitionService.verify_face(image_data, employee)
            
            if not face_verified:
                return JsonResponse({
                    'success': False, 
                    'error': 'Face verification failed'
                })
            
            # Save attendance record
            attendance = Attendance.objects.create(
                employee=employee,
                location_lat=user_lat,
                location_long=user_long,
                verified=True
            )
            
            # Save image (convert base64 to ImageField)
            from django.core.files.base import ContentFile
            import base64
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'attendance_{attendance.id}.{ext}')
            attendance.image.save(f'attendance_{attendance.id}.{ext}', data, save=True)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})




def register_view(request):
    return render(request, 'attendanceMarker/register.html')

def mark_view(request):
    return render(request, 'attendanceMarker/mark.html')