from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('login/', views.login, name="login"),
    path('planning/', views.Planning, name="planning"),
]