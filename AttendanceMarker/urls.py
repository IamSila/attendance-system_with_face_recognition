from django.urls import path
from . import views

urlpatterns = [
    path('register_face/', views.register_face, name='register_face'),
    #path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('register/', views.register_view, name='register_view'),
    path('mark/', views.mark_view, name='mark_view'),
]