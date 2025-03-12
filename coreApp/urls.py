from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('login/', views.Login, name="login"),
    path('register', views.Register, name="register"),
    path('logout/', views.Logout, name="logout"),
    path('api/tasks/', views.get_tasks, name="get_tasks"),
    path('planning/', views.Planning, name="planning"),
    path('dashboard/', views.Dashboard, name="dashboard"),
]