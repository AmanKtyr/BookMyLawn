from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='superadmin_dashboard'),
    path('login/', views.superadmin_login, name='superadmin_login'),
    path('logout/', views.superadmin_logout, name='superadmin_logout'),
]
