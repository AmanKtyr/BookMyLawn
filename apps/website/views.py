from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Vendor, Category, RealWedding, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, UserProfile, WeddingChecklist, BlogPost

def index(request):
    featured_vendors = Vendor.objects.filter(is_premium=True).order_by('-created_at')[:6]
    if not featured_vendors.exists():
        featured_vendors = Vendor.objects.all().order_by('-created_at')[:6]
    categories = Category.objects.all()
    real_weddings = RealWedding.objects.all().order_by('-date')[:3]
    recent_blogs = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:3]
    return render(request, 'website/index.html', {
        'featured_vendors': featured_vendors,
        'categories': categories,
        'real_weddings': real_weddings,
        'recent_blogs': recent_blogs,
    })

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
            Q(category__name__icontains=query) |
            Q(location__icontains=query) |
            Q(address__icontains=query)
        )
        
    if city:
        all_vendors = all_vendors.filter(location__icontains=city)
        
    if category_slug:
        all_vendors = all_vendors.filter(category__slug=category_slug)

    selected_category = Category.objects.filter(slug=category_slug).first() if category_slug else None

    # Dynamic SEO titles and descriptions
    if view_type == 'venues':
        if city:
            page_title = f"Top Wedding Lawns & Banquet Halls in {city} | BookMyLawn"
            meta_description = f"Find and book the best wedding lawns, marriage gardens, and luxury banquet halls in {city}. Verified venues, transparent prices, guest capacity & real reviews."
        else:
            page_title = "Best Wedding Lawns, Banquet Halls & Venues in India | BookMyLawn"
            meta_description = "Explore top wedding lawns, marriage halls, open-air party plots, and banquet venues across major Indian cities with verified reviews and transparent prices."
    elif selected_category:
        if city:
            page_title = f"Best Wedding {selected_category.name} in {city} | BookMyLawn"
            meta_description = f"Discover verified wedding {selected_category.name.lower()} in {city}. Compare packages, view portfolios, check ratings, and request free quotes at BookMyLawn."
        else:
            page_title = f"Top Wedding {selected_category.name} in India | BookMyLawn"
            meta_description = f"Book verified wedding {selected_category.name.lower()} across India. Explore top-rated professionals, transparent prices, customer reviews, and portfolios."
    elif city:
        page_title = f"Wedding Venues & Vendors in {city} | BookMyLawn"
        meta_description = f"Looking for wedding lawns, banquet halls, photographers & caterers in {city}? Browse top-rated wedding vendors in {city} with verified reviews at BookMyLawn."
    else:
        page_title = "Search Wedding Venues, Lawns & Vendors | BookMyLawn"
        meta_description = "Find verified wedding lawns, luxury banquet halls, wedding photographers, bridal makeup artists, decorators, and caterers across India at BookMyLawn."

    context = {
        'vendors': all_vendors, 
        'categories': categories, 
        'view_type': view_type,
        'selected_city': city,
        'selected_date': date,
        'selected_category': selected_category,
        'page_title': page_title,
        'meta_description': meta_description,
        'vendor_count': all_vendors.count(),
    }
    return render(request, 'website/vendors.html', context)

def vendor_details(request, uuid):
    vendor = get_object_or_404(Vendor, uuid_field=uuid)
    related_vendors = Vendor.objects.filter(category=vendor.category).exclude(id=vendor.id)[:4]
    return render(request, 'website/vendor-details.html', {
        'vendor': vendor,
        'related_vendors': related_vendors
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Valued Guest')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'General Inquiry')
        message = request.POST.get('message')
        from django.contrib import messages
        messages.success(request, f"Thank you, {name}! Your message has been received. Our wedding concierge team will get back to you within 2 hours.")
        return redirect('contact')
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
    q = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    posts = BlogPost.objects.filter(is_published=True)
    if q:
        posts = posts.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        )
    if tag:
        posts = posts.filter(
            Q(title__icontains=tag) | Q(content__icontains=tag)
        )
    posts = posts.order_by('-created_at')
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:4]
    
    page_title = "Wedding Planning Blog, Guides & Venue Advice | BookMyLawn"
    if q:
        page_title = f"Search Results for '{q}' | Wedding Blog | BookMyLawn"
    elif tag:
        page_title = f"{tag.title()} Guides & Ideas | BookMyLawn Blog"

    return render(request, 'website/blog.html', {
        'posts': posts,
        'query': q,
        'selected_tag': tag,
        'recent_posts': recent_posts,
        'page_title': page_title,
    })

def blog_details(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-created_at')[:4]
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
                task = WeddingChecklist.objects.create(
                    user=request.user,
                    task_name=task_name,
                    due_date=due_date if due_date else None
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == 'true':
                    due_date_str = task.due_date.strftime('%d %b %Y') if task.due_date else None
                    return JsonResponse({
                        'status': 'success', 
                        'task_id': task.id, 
                        'task_name': task.task_name, 
                        'due_date': due_date_str
                    })
            return redirect('user_dashboard')
            
        elif action == 'toggle_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(WeddingChecklist, id=task_id, user=request.user)
            task.is_completed = not task.is_completed
            task.save()
            return JsonResponse({'status': 'success', 'is_completed': task.is_completed})
            
        elif action == 'add_guest':
            from .models import Guest
            name = request.POST.get('guest_name')
            group = request.POST.get('group', 'family')
            rsvp = request.POST.get('rsvp', 'pending')
            meal = request.POST.get('meal', 'any')
            if name:
                Guest.objects.create(
                    user=request.user,
                    name=name,
                    group=group,
                    rsvp_status=rsvp,
                    meal_preference=meal
                )
            return redirect('user_dashboard')
            
        elif action == 'delete_guest':
            from .models import Guest
            guest_id = request.POST.get('guest_id')
            guest = get_object_or_404(Guest, id=guest_id, user=request.user)
            guest.delete()
            return redirect('user_dashboard')

    # Fetch dashboard data
    checklist_items = WeddingChecklist.objects.filter(user=request.user).order_by('due_date', 'id')
    from .models import Guest
    guests = Guest.objects.filter(user=request.user).order_by('-created_at')
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
        'guests': guests,
    }
    return render(request, 'website/user-dashboard.html', context)


# --- SEO, Legal & Trust Views ---

def faq_view(request):
    return render(request, 'website/faq.html')

def privacy_policy(request):
    return render(request, 'website/privacy-policy.html')

def terms_of_service(request):
    return render(request, 'website/terms-of-service.html')

from xml.sax.saxutils import escape

def sitemap_xml(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    pages = [
        {'loc': f"{base_url}/", 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': f"{base_url}/vendors/", 'changefreq': 'daily', 'priority': '0.9'},
        {'loc': f"{base_url}/vendors/?type=venues", 'changefreq': 'daily', 'priority': '0.9'},
        {'loc': f"{base_url}/real-weddings/", 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': f"{base_url}/blog/", 'changefreq': 'daily', 'priority': '0.85'},
        {'loc': f"{base_url}/about-us/", 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': f"{base_url}/contact/", 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': f"{base_url}/faq/", 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': f"{base_url}/planning-tools/", 'changefreq': 'weekly', 'priority': '0.85'},
        {'loc': f"{base_url}/privacy-policy/", 'changefreq': 'yearly', 'priority': '0.4'},
        {'loc': f"{base_url}/terms-of-service/", 'changefreq': 'yearly', 'priority': '0.4'},
    ]

    for cat in Category.objects.all():
        pages.append({
            'loc': f"{base_url}/vendors/?category={cat.slug}",
            'changefreq': 'weekly',
            'priority': '0.85'
        })

    popular_cities = ['Delhi', 'Mumbai', 'Lucknow', 'Jaipur', 'Bangalore', 'Udaipur', 'Goa', 'Chandigarh']
    for city in popular_cities:
        pages.append({
            'loc': f"{base_url}/vendors/?city={city}",
            'changefreq': 'weekly',
            'priority': '0.85'
        })
        pages.append({
            'loc': f"{base_url}/vendors/?type=venues&city={city}",
            'changefreq': 'weekly',
            'priority': '0.85'
        })

    for v in Vendor.objects.all():
        pages.append({
            'loc': f"{base_url}/vendor/{v.uuid_field}/",
            'lastmod': v.created_at.strftime('%Y-%m-%d') if v.created_at else None,
            'changefreq': 'weekly',
            'priority': '0.8',
            'image': f"{base_url}{v.image.url}" if v.image else None,
            'image_title': f"{v.name} - Wedding Lawn in {v.location}"
        })

    for b in BlogPost.objects.filter(is_published=True):
        pages.append({
            'loc': f"{base_url}/blog/{b.slug}/",
            'lastmod': b.created_at.strftime('%Y-%m-%d') if b.created_at else None,
            'changefreq': 'monthly',
            'priority': '0.8',
            'image': f"{base_url}{b.image.url}" if b.image else None,
            'image_title': b.title
        })

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
    ]
    for p in pages:
        xml_lines.append('  <url>')
        loc_escaped = escape(str(p['loc']))
        xml_lines.append(f"    <loc>{loc_escaped}</loc>")
        if p.get('lastmod'):
            xml_lines.append(f"    <lastmod>{p['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{p['priority']}</priority>")
        if p.get('image'):
            img_loc = escape(str(p['image']))
            xml_lines.append('    <image:image>')
            xml_lines.append(f"      <image:loc>{img_loc}</image:loc>")
            if p.get('image_title'):
                xml_lines.append(f"      <image:title>{escape(str(p['image_title']))}</image:title>")
            xml_lines.append('    </image:image>')
        xml_lines.append('  </url>')
    xml_lines.append('</urlset>')

    return HttpResponse('\n'.join(xml_lines), content_type='application/xml')

def robots_txt(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /superadmin/
Disallow: /vendor/
Disallow: /dashboard/
Disallow: /cart/
Disallow: /checkout/
Disallow: /add-to-cart/
Disallow: /add-to-wishlist/
Disallow: /submit-inquiry/
Disallow: /submit-review/

Sitemap: {base_url}/sitemap.xml
"""
    return HttpResponse(content.strip(), content_type='text/plain')

def wedding_tools(request):
    return render(request, 'website/wedding-tools.html')
