from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vendors/', views.vendors, name='vendors'),
    path('vendor/<int:id>/', views.vendor_details, name='vendor_details'),
    path('contact/', views.contact, name='contact'),
    path('real-weddings/', views.real_weddings, name='real_weddings'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='user_logout'),
    path('register/', views.register_view, name='register'),
    path('vendor-register/', views.vendor_register_view, name='vendor_register'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('submit-inquiry/', views.submit_inquiry, name='submit_inquiry'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('about-us/', views.about_us, name='about_us'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_details, name='blog_details'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]
