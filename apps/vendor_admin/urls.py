from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='vendor_dashboard'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.vendor_logout, name='vendor_logout'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
    path('inquiries/', views.vendor_inquiries, name='vendor_inquiries'),
    path('inquiries/<int:inquiry_id>/update-status/', views.update_inquiry_status, name='update_inquiry_status'),
    path('reviews/', views.vendor_reviews, name='vendor_reviews'),
    path('reviews/<int:review_id>/reply/', views.reply_to_review, name='reply_to_review'),
    path('membership/', views.vendor_subscription, name='vendor_subscription'),
    path('membership/upgrade/', views.request_membership_upgrade, name='request_membership_upgrade'),
    path('portfolio/', views.vendor_portfolio, name='vendor_portfolio'),
    path('portfolio/delete/<int:image_id>/', views.delete_portfolio_image, name='delete_portfolio_image'),
    path('portfolio/set-cover/<int:image_id>/', views.set_cover_image, name='set_cover_image'),
    path('calendar/', views.vendor_calendar, name='vendor_calendar'),
    path('calendar/update-date/', views.update_calendar_date, name='update_calendar_date'),
    path('calendar/delete-date/<int:date_id>/', views.delete_calendar_date, name='delete_calendar_date'),
    path('support/', views.vendor_support, name='vendor_support'),
]
