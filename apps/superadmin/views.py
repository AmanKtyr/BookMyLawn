from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.website.models import Vendor, Review

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superadmin, login_url='superadmin_login')
def dashboard(request):
    total_vendors = Vendor.objects.count()
    premium_vendors = Vendor.objects.filter(is_premium=True).count()
    verified_vendors = Vendor.objects.filter(is_verified=True).count()
    recent_vendors = Vendor.objects.order_by('-created_at')[:5]
    
    total_reviews = Review.objects.count()
    
    context = {
        'total_vendors': total_vendors,
        'premium_vendors': premium_vendors,
        'verified_vendors': verified_vendors,
        'recent_vendors': recent_vendors,
        'total_reviews': total_reviews,
    }
    return render(request, 'superadmin/index.html', context)

def superadmin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('superadmin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('superadmin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a superadmin.")
            
    return render(request, 'superadmin/login.html')

def superadmin_logout(request):
    logout(request)
    return redirect('superadmin_login')
