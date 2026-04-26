from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='superadmin_dashboard'),
    path('login/', views.superadmin_login, name='superadmin_login'),
    path('categories/', views.categories_list, name='superadmin_categories'),
    path('categories/add/', views.category_add, name='superadmin_category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='superadmin_category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='superadmin_category_delete'),
    path('vendors/', views.vendors_list, name='superadmin_vendors'),
    path('vendors/add/', views.vendor_add, name='superadmin_vendor_add'),
    path('wedding-stories/', views.wedding_stories_list, name='superadmin_wedding_stories'),
    path('wedding-stories/add/', views.wedding_story_add, name='superadmin_wedding_story_add'),
    path('partners/', views.partners_list, name='superadmin_partners'),
    path('users/', views.users_list, name='superadmin_users'),
    path('reviews/', views.reviews_list, name='superadmin_reviews'),
    path('inquiries/', views.inquiries_list, name='superadmin_inquiries'),
    path('logout/', views.superadmin_logout, name='superadmin_logout'),
]
