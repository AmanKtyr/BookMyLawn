from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vendors/', views.vendors, name='vendors'),
    path('vendor/<int:id>/', views.vendor_details, name='vendor_details'),
    path('contact/', views.contact, name='contact'),
    path('real-weddings/', views.real_weddings, name='real_weddings'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('vendor-register/', views.vendor_register_view, name='vendor_register'),
]
