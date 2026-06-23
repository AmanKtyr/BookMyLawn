from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.website.models import Vendor, Inquiry, Review, OrderItem

def is_vendor(user):
    return user.is_authenticated and hasattr(user, 'vendor_profile')

@user_passes_test(is_vendor, login_url='vendor_login')
def dashboard(request):
    vendor = request.user.vendor_profile
    total_inquiries = Inquiry.objects.filter(vendor=vendor).count()
    new_inquiries = Inquiry.objects.filter(vendor=vendor, status='new').count()
    total_reviews = Review.objects.filter(vendor=vendor).count()
    recent_inquiries = Inquiry.objects.filter(vendor=vendor).order_by('-created_at')[:5]
    
    # 1. Inquiries Trend (Last 6 Months)
    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    import datetime
    
    six_months_ago = datetime.date.today() - datetime.timedelta(days=180)
    inquiry_trend = Inquiry.objects.filter(vendor=vendor, created_at__gte=six_months_ago) \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')
    
    trend_labels = [item['month'].strftime('%b') for item in inquiry_trend]
    trend_counts = [item['count'] for item in inquiry_trend]
    
    # 2. Ratings Distribution
    rating_stats = Review.objects.filter(vendor=vendor) \
        .values('rating') \
        .annotate(count=Count('id')) \
        .order_by('-rating')
    
    rating_labels = [f"{i} Star" for i in range(5, 0, -1)]
    rating_counts = [0] * 5
    for rs in rating_stats:
        if 1 <= rs['rating'] <= 5:
            rating_counts[5 - rs['rating']] = rs['count']

    # 3. Recent Reviews for the card
    recent_reviews = Review.objects.filter(vendor=vendor).order_by('-created_at')[:3]
    
    # 4. Potential Revenue (Simulation)
    # Simple logic: Price starting * closed inquiries or similar
    potential_revenue = Inquiry.objects.filter(vendor=vendor, status='closed').count() * float(vendor.price_starting)

    context = {
        'vendor': vendor,
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'total_reviews': total_reviews,
        'recent_inquiries': recent_inquiries,
        'recent_reviews': recent_reviews,
        'potential_revenue': potential_revenue,
        'trend_labels': trend_labels,
        'trend_counts': trend_counts,
        'rating_labels': rating_labels,
        'rating_counts': rating_counts,
    }
    return render(request, 'vendor_admin/index.html', context)

def vendor_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'vendor_profile'):
            return redirect('vendor_dashboard')
        elif request.user.is_superuser:
            return redirect('superadmin_dashboard')
            
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try finding user by email first
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=login_input)
            username = user_obj.username
        except User.DoesNotExist:
            username = login_input
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'vendor_profile'):
                login(request, user)
                return redirect('vendor_dashboard')
            else:
                messages.error(request, "This account is not a vendor account.")
        else:
            messages.error(request, "Invalid credentials or account not found.")
            
    return render(request, 'vendor_admin/login.html')

def vendor_logout(request):
    logout(request)
    return redirect('vendor_login')

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_profile(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        # Basic Info
        vendor.name = request.POST.get('name')
        vendor.location = request.POST.get('location')
        vendor.address = request.POST.get('address')
        vendor.price_starting = request.POST.get('price_starting', 0)
        
        # Specifics
        vendor.veg_price = request.POST.get('veg_price', 0)
        vendor.non_veg_price = request.POST.get('non_veg_price', 0)
        vendor.capacity = request.POST.get('capacity', 0)
        vendor.rooms = request.POST.get('rooms', 0)
        
        # Details
        vendor.description = request.POST.get('description')
        vendor.amenities = request.POST.get('amenities')
        vendor.map_link = request.POST.get('map_link')
        vendor.experience_years = request.POST.get('experience_years', 0)
        
        if request.FILES.get('image'):
            vendor.image = request.FILES.get('image')
            
        vendor.save()
        
        # Handle Gallery Uploads
        gallery_images = request.FILES.getlist('gallery_images')
        from apps.website.models import VendorImage
        for img in gallery_images:
            VendorImage.objects.create(vendor=vendor, image=img)
            
        messages.success(request, 'Profile and Gallery updated successfully.')
        return redirect('vendor_profile')
        
    gallery = vendor.gallery.all()
    return render(request, 'vendor_admin/profile.html', {'vendor': vendor, 'gallery': gallery})

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_inquiries(request):
    vendor = request.user.vendor_profile
    inquiries = Inquiry.objects.filter(vendor=vendor).order_by('-created_at')
    return render(request, 'vendor_admin/inquiries.html', {'inquiries': inquiries})

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_reviews(request):
    vendor = request.user.vendor_profile
    reviews = Review.objects.filter(vendor=vendor).order_by('-created_at')
    return render(request, 'vendor_admin/reviews.html', {'reviews': reviews})

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_subscription(request):
    vendor = request.user.vendor_profile
    return render(request, 'vendor_admin/subscription.html', {'vendor': vendor})

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_support(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        messages.success(request, "Your support ticket has been raised. Our team will contact you shortly.")
        return redirect('vendor_support')
    return render(request, 'vendor_admin/support.html', {'vendor': vendor})
