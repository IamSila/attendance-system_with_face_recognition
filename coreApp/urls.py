from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('base/', views.Base, name='base'),
    path('register/', views.Register, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('planning/', views.Planning, name='planning'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('profile/', views.Profile, name='profile'),
    path('profileUpdate/', views.UpdateProfile, name='profileUpdate'),
    path('api/tasks/', views.get_tasks, name='get_tasks'),
    path('markAttendance/', views.MarkAttendance, name='markAttendance'),
    # path('markAttendance/<str:class_name>/', views.MarkAttendance, name='attendClass'),
    path('recognize-face/', views.recognize_face, name='recognize_face'),
]