from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='vendor_dashboard'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.vendor_logout, name='vendor_logout'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
    path('inquiries/', views.vendor_inquiries, name='vendor_inquiries'),
    path('reviews/', views.vendor_reviews, name='vendor_reviews'),
    path('membership/', views.vendor_subscription, name='vendor_subscription'),
    path('support/', views.vendor_support, name='vendor_support'),
]
