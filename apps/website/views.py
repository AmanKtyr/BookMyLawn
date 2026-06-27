from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Vendor, Category, RealWedding, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, UserProfile, WeddingChecklist, BlogPost

def index(request):
    # Fetch some premium vendors for the homepage
    featured_vendors = Vendor.objects.filter(is_premium=True).order_by('-created_at')[:3]
    return render(request, 'website/index.html', {'featured_vendors': featured_vendors})

def vendors(request):
    all_vendors = Vendor.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    # Handle search parameters
    query = request.GET.get('q')
    city = request.GET.get('city')
    category_slug = request.GET.get('category')
    view_type = request.GET.get('type')
    
    date = request.GET.get('date')

    if view_type == 'venues':
        all_vendors = all_vendors.filter(category__slug='venues')
    elif view_type == 'vendors':
        all_vendors = all_vendors.exclude(category__slug='venues')
    
    if query:
        all_vendors = all_vendors.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
        
    if city:
        all_vendors = all_vendors.filter(location__icontains=city)
        
    if category_slug:
        all_vendors = all_vendors.filter(category__slug=category_slug)
        
    context = {
        'vendors': all_vendors, 
        'categories': categories, 
        'view_type': view_type,
        'selected_city': city,
        'selected_date': date,
    }
    return render(request, 'website/vendors.html', context)

def vendor_details(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    related_vendors = Vendor.objects.filter(category=vendor.category).exclude(id=id)[:4]
    return render(request, 'website/vendor-details.html', {
        'vendor': vendor,
        'related_vendors': related_vendors
    })

def contact(request):
    return render(request, 'website/contact.html')

def real_weddings(request):
    weddings = RealWedding.objects.all().order_by('-date')
    return render(request, 'website/real-weddings.html', {'weddings': weddings})

def login_view(request):
    from django.contrib.auth import authenticate, login
    user_type = request.GET.get('type')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # In Django, authenticate usually takes 'username'. 
        # If the email is the username, we use it. 
        # Let's try to find the user by email first.
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = email # Fallback to email as username
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'vendor_profile'):
                return redirect('vendor_dashboard')
            elif user.is_superuser:
                return redirect('superadmin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            from django.contrib import messages
            # Check if this email has a pending vendor request
            from .models import VendorRequest
            if VendorRequest.objects.filter(email=email, status='pending').exists():
                messages.info(request, "Your vendor registration is still pending approval. Please wait for the administrator to review your profile.")
            else:
                messages.error(request, "Invalid email or password.")
            
    return render(request, 'website/login.html', {'user_type': user_type})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')


def register_view(request):
    if request.method == 'POST':
        from django.contrib.auth.models import User
        from django.contrib import messages
        from django.contrib.auth import login
        from .models import UserProfile
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'website/register.html')
            
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Account with this email already exists.")
            return render(request, 'website/register.html')
            
        try:
            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.save()
            
            # Create user profile
            UserProfile.objects.create(user=user, phone=phone)
            
            # Auto login
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to BookMyLawn.")
            return redirect('user_dashboard')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            
    return render(request, 'website/register.html')

def vendor_register_view(request):
    from .models import VendorRequest, Category
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        category = request.POST.get('category')
        owner_name = request.POST.get('owner_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        address = request.POST.get('address', '')
        price_starting = request.POST.get('price_starting', 0)
        website_link = request.POST.get('website_link', '')
        experience_years = request.POST.get('experience_years', 0)
        description = request.POST.get('description', '')
        business_image = request.FILES.get('business_image')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            from django.contrib import messages
            messages.error(request, "Passwords do not match.")
            categories = Category.objects.all()
            return render(request, 'website/vendor-register.html', {'categories': categories})

        VendorRequest.objects.create(
            business_name=business_name,
            category=category,
            owner_name=owner_name,
            email=email,
            phone=phone,
            city=city,
            address=address,
            price_starting=price_starting,
            website_link=website_link,
            experience_years=experience_years,
            description=description,
            business_image=business_image,
            password=password
        )
        return redirect('registration_success')

    categories = Category.objects.all()
    return render(request, 'website/vendor-register.html', {'categories': categories})

def registration_success(request):
    return render(request, 'website/registration-success.html')

@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        event_date = request.POST.get('event_date')
        location = request.POST.get('location')
        
        if not event_date or not location:
            return JsonResponse({'status': 'error', 'message': 'Please select date and location first.'})
            
        vendor = get_object_or_404(Vendor, id=vendor_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if already in cart
        if CartItem.objects.filter(cart=cart, vendor=vendor).exists():
            return JsonResponse({'status': 'info', 'message': 'Vendor already in cart.'})
            
        CartItem.objects.create(
            cart=cart,
            vendor=vendor,
            event_date=event_date,
            location=location
        )
        
        cart_count = cart.items.count()
        return JsonResponse({'status': 'success', 'message': 'Added to cart.', 'cart_count': cart_count})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@login_required(login_url='/login/')
def add_to_wishlist(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        vendor = get_object_or_404(Vendor, id=vendor_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        # Check if already in wishlist
        if WishlistItem.objects.filter(wishlist=wishlist, vendor=vendor).exists():
            return JsonResponse({'status': 'info', 'message': 'Vendor already in wishlist.'})
            
        WishlistItem.objects.create(wishlist=wishlist, vendor=vendor)
        return JsonResponse({'status': 'success', 'message': 'Added to wishlist.'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@login_required(login_url='/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.vendor.price_starting for item in items)
    return render(request, 'website/shop-cart.html', {'cart_items': items, 'total': total})

@login_required(login_url='/login/')
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    if request.method == 'POST':
        if not items.exists():
            return redirect('cart')
            
        total = sum(item.vendor.price_starting for item in items)
        order = Order.objects.create(user=request.user, total_amount=total, is_paid=True)
        
        for item in items:
            OrderItem.objects.create(
                order=order,
                vendor=item.vendor,
                event_date=item.event_date,
                location=item.location,
                price=item.vendor.price_starting
            )
            
        # Clear cart
        items.delete()
        
        return render(request, 'website/order-success.html', {'order': order})
        
    total = sum(item.vendor.price_starting for item in items)
    return render(request, 'website/checkout.html', {'cart_items': items, 'total': total})

def submit_inquiry(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        vendor = get_object_or_404(Vendor, id=vendor_id)
        
        customer_name = request.POST.get('name')
        customer_email = request.POST.get('email')
        customer_phone = request.POST.get('phone')
        event_date = request.POST.get('event_date')
        message = request.POST.get('message', f'Inquiry for {vendor.name}')
        
        from .models import Inquiry
        Inquiry.objects.create(
            vendor=vendor,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            event_date=event_date,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Your inquiry has been sent to {vendor.name}. They will contact you shortly!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def registration_success(request):
    return render(request, 'website/registration-success.html')

from django.contrib.auth.decorators import login_required
from .models import Review

@login_required(login_url='/login/')
def submit_review(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        vendor = get_object_or_404(Vendor, id=vendor_id)
        
        # Check if user already reviewed
        if Review.objects.filter(vendor=vendor, user=request.user).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already reviewed this vendor.'})
            
        Review.objects.create(
            vendor=vendor,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({'status': 'success', 'message': 'Your review has been published successfully!'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def about_us(request):
    return render(request, 'website/about.html')

def blog(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'website/blog.html', {'posts': posts})

def blog_details(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-created_at')[:3]
    return render(request, 'website/blog-details.html', {'post': post, 'recent_posts': recent_posts})

@login_required(login_url='/login/')
def user_dashboard(request):
    # Ensure UserProfile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle profile updates
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            profile.partner_name = request.POST.get('partner_name', profile.partner_name)
            profile.phone = request.POST.get('phone', profile.phone)
            wedding_date = request.POST.get('wedding_date')
            if wedding_date:
                profile.wedding_date = wedding_date
            profile.budget = request.POST.get('budget', profile.budget)
            profile.save()
            return redirect('user_dashboard')
            
        elif action == 'add_task':
            task_name = request.POST.get('task_name')
            due_date = request.POST.get('due_date')
            if task_name:
                WeddingChecklist.objects.create(
                    user=request.user,
                    task_name=task_name,
                    due_date=due_date if due_date else None
                )
            return redirect('user_dashboard')
            
        elif action == 'toggle_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(WeddingChecklist, id=task_id, user=request.user)
            task.is_completed = not task.is_completed
            task.save()
            return JsonResponse({'status': 'success', 'is_completed': task.is_completed})

    # Fetch dashboard data
    checklist_items = WeddingChecklist.objects.filter(user=request.user).order_by('due_date', 'id')
    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlist_items = wishlist.items.all() if wishlist else []
    
    from .models import Inquiry
    inquiries = Inquiry.objects.filter(user=request.user).order_by('-created_at')
    
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []
    
    context = {
        'profile': profile,
        'checklist_items': checklist_items,
        'wishlist_items': wishlist_items,
        'inquiries': inquiries,
        'cart_items': cart_items,
    }
    return render(request, 'website/user-dashboard.html', context)
