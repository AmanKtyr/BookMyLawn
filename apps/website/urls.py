from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vendors/', views.vendors, name='vendors'),
    path('vendor/<int:id>/', views.vendor_details, name='vendor_details'),
    path('contact/', views.contact, name='contact'),
]
