from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.website.models import Vendor, Inquiry, Review, OrderItem, SupportTicket, VendorImage, VendorAvailability

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
        vendor.description = request.POST.get('description', '')
        vendor.amenities = request.POST.get('amenities', '')
        vendor.map_link = request.POST.get('map_link', '')
        vendor.website_link = request.POST.get('website_link', '')
        vendor.facebook_link = request.POST.get('facebook_link', '')
        vendor.instagram_link = request.POST.get('instagram_link', '')
        vendor.experience_years = request.POST.get('experience_years', 0)
        
        # Business Policies
        vendor.cancellation_policy = request.POST.get('cancellation_policy', '')
        vendor.payment_terms = request.POST.get('payment_terms', '')
        vendor.travel_policy = request.POST.get('travel_policy', '')
        
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
    
    # Filter by Status
    status_filter = request.GET.get('status', '')
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
        
    # Search by Name, Email, or Phone
    search_query = request.GET.get('search', '')
    if search_query:
        from django.db.models import Q
        inquiries = inquiries.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
        
    context = {
        'inquiries': inquiries,
        'current_status': status_filter,
        'current_search': search_query
    }
    return render(request, 'vendor_admin/inquiries.html', context)

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
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        attachment = request.FILES.get('attachment')
        
        if subject and message:
            SupportTicket.objects.create(
                vendor=vendor,
                subject=subject,
                message=message,
                attachment=attachment
            )
            messages.success(request, "Your support ticket has been raised successfully. Our team will review your request and get back to you shortly.")
        else:
            messages.error(request, "Please fill in all required fields.")
        return redirect('vendor_support')

    tickets = vendor.support_tickets.all()
    return render(request, 'vendor_admin/support.html', {'vendor': vendor, 'tickets': tickets})


@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_portfolio(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        images = request.FILES.getlist('gallery_images')
        caption = request.POST.get('caption', '').strip()
        if images:
            count = 0
            for img in images:
                VendorImage.objects.create(vendor=vendor, image=img, caption=caption)
                count += 1
            messages.success(request, f"Successfully uploaded {count} photo(s) to your portfolio.")
        else:
            messages.error(request, "Please select at least one image to upload.")
        return redirect('vendor_portfolio')
    
    gallery = vendor.gallery.all().order_by('-created_at')
    return render(request, 'vendor_admin/portfolio.html', {
        'vendor': vendor,
        'gallery': gallery,
        'total_photos': gallery.count(),
    })

@user_passes_test(is_vendor, login_url='vendor_login')
def delete_portfolio_image(request, image_id):
    vendor = request.user.vendor_profile
    img = get_object_or_404(VendorImage, id=image_id, vendor=vendor)
    img.delete()
    messages.success(request, "Photo removed from portfolio.")
    return redirect('vendor_portfolio')

@user_passes_test(is_vendor, login_url='vendor_login')
def set_cover_image(request, image_id):
    vendor = request.user.vendor_profile
    img = get_object_or_404(VendorImage, id=image_id, vendor=vendor)
    vendor.image = img.image
    vendor.save()
    messages.success(request, "This photo has been set as your primary listing cover.")
    return redirect('vendor_portfolio')

@user_passes_test(is_vendor, login_url='vendor_login')
def vendor_calendar(request):
    vendor = request.user.vendor_profile
    import datetime
    import calendar
    
    today = datetime.date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    # Prev / Next month calculations
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_name = calendar.month_name[month]
    
    # Days in month
    cal = calendar.Calendar(firstweekday=6) # Start Sunday
    month_days = cal.monthdatescalendar(year, month)
    
    # Existing availability records for this vendor in this month range
    start_date = month_days[0][0]
    end_date = month_days[-1][-1]
    
    avail_qs = VendorAvailability.objects.filter(vendor=vendor, date__range=(start_date, end_date))
    avail_map = {a.date: a for a in avail_qs}
    
    # Also check inquiries with event_date in this month range
    inquiries_qs = Inquiry.objects.filter(vendor=vendor, event_date__range=(start_date, end_date))
    inquiry_map = {}
    for inq in inquiries_qs:
        inquiry_map.setdefault(inq.event_date, []).append(inq)

    # Prepare structured weeks data
    weeks_data = []
    for week in month_days:
        week_days = []
        for day in week:
            is_current_month = (day.month == month)
            avail = avail_map.get(day)
            inqs = inquiry_map.get(day, [])
            
            status = avail.status if avail else 'available'
            note = avail.note if avail else ''
            
            week_days.append({
                'date': day,
                'date_str': day.strftime('%Y-%m-%d'),
                'day_num': day.day,
                'is_current_month': is_current_month,
                'is_today': (day == today),
                'is_past': (day < today),
                'status': status,
                'note': note,
                'avail_id': avail.id if avail else None,
                'inquiries_count': len(inqs),
            })
        weeks_data.append(week_days)

    # Monthly Stats
    current_month_avails = [a for a in avail_qs if a.date.month == month]
    booked_count = sum(1 for a in current_month_avails if a.status == 'booked')
    tentative_count = sum(1 for a in current_month_avails if a.status == 'tentative')
    blocked_count = sum(1 for a in current_month_avails if a.status == 'blocked')
    
    # Upcoming Booked / Blocked / Tentative events list
    upcoming_dates = VendorAvailability.objects.filter(
        vendor=vendor, date__gte=today
    ).order_by('date')[:12]

    return render(request, 'vendor_admin/calendar.html', {
        'vendor': vendor,
        'year': year,
        'month': month,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'weeks_data': weeks_data,
        'booked_count': booked_count,
        'tentative_count': tentative_count,
        'blocked_count': blocked_count,
        'upcoming_dates': upcoming_dates,
        'today': today,
    })

@user_passes_test(is_vendor, login_url='vendor_login')
def update_calendar_date(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        date_str = request.POST.get('date')
        status = request.POST.get('status', 'booked')
        note = request.POST.get('note', '').strip()
        
        import datetime
        try:
            parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format.")
            return redirect('vendor_calendar')
            
        if status == 'available':
            VendorAvailability.objects.filter(vendor=vendor, date=parsed_date).delete()
            messages.success(request, f"{parsed_date.strftime('%d %b %Y')} marked as Available.")
        else:
            avail, created = VendorAvailability.objects.update_or_create(
                vendor=vendor,
                date=parsed_date,
                defaults={'status': status, 'note': note}
            )
            messages.success(request, f"{parsed_date.strftime('%d %b %Y')} updated to {avail.get_status_display()}.")
            
        return redirect(f"{redirect('vendor_calendar').url}?year={parsed_date.year}&month={parsed_date.month}")
        
    return redirect('vendor_calendar')

@user_passes_test(is_vendor, login_url='vendor_login')
def delete_calendar_date(request, date_id):
    vendor = request.user.vendor_profile
    avail = get_object_or_404(VendorAvailability, id=date_id, vendor=vendor)
    y, m = avail.date.year, avail.date.month
    avail.delete()
    messages.success(request, "Date reset to Available.")
    return redirect(f"{redirect('vendor_calendar').url}?year={y}&month={m}")
