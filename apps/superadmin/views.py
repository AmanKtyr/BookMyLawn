from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.website.models import Vendor, Review

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superadmin, login_url='superadmin_login')
def dashboard(request):
    from apps.website.models import Category
    total_vendors = Vendor.objects.count()
    premium_vendors = Vendor.objects.filter(is_premium=True).count()
    verified_vendors = Vendor.objects.filter(is_verified=True).count()
    recent_vendors = Vendor.objects.order_by('-created_at')[:5]
    total_reviews = Review.objects.count()

    # Data for Graphs
    categories = Category.objects.all()
    cat_names = [c.name for c in categories]
    cat_counts = [c.vendors.count() for c in categories]
    
    context = {
        'total_vendors': total_vendors,
        'premium_vendors': premium_vendors,
        'verified_vendors': verified_vendors,
        'recent_vendors': recent_vendors,
        'total_reviews': total_reviews,
        'cat_names': cat_names,
        'cat_counts': cat_counts,
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

@user_passes_test(is_superadmin, login_url='superadmin_login')
def categories_list(request):
    from apps.website.models import Category
    categories = Category.objects.all().order_by('name')
    return render(request, 'superadmin/categories.html', {'categories': categories})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def vendors_list(request):
    vendors = Vendor.objects.all().order_by('-created_at')
    return render(request, 'superadmin/vendors.html', {'vendors': vendors})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def wedding_stories_list(request):
    from apps.website.models import RealWedding
    stories = RealWedding.objects.all().order_by('-date')
    return render(request, 'superadmin/wedding_stories.html', {'stories': stories})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def partners_list(request):
    from apps.website.models import VendorRequest
    requests = VendorRequest.objects.all().order_by('-created_at')
    return render(request, 'superadmin/partners.html', {'requests': requests})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def partner_approve(request, pk):
    from apps.website.models import VendorRequest, Vendor, Category
    req = VendorRequest.objects.get(pk=pk)
    
    # Check if vendor already exists
    if not Vendor.objects.filter(name=req.business_name).exists():
        # Get or create category
        from django.utils.text import slugify
        cat, _ = Category.objects.get_or_create(name=req.category, defaults={'slug': slugify(req.category)})
        
        # Create User for Vendor
        from django.contrib.auth.models import User
        import random
        import string
        
        # Generate a random password if none provided
        password = req.password or ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        username = slugify(req.business_name).replace('-', '_')
        
        # Ensure username is unique
        if User.objects.filter(username=username).exists():
            username = f"{username}_{random.randint(10, 99)}"
            
        user = User.objects.create_user(username=username, email=req.email, password=password)
        
        vendor = Vendor.objects.create(
            user=user,
            name=req.business_name,
            category=cat,
            location=req.city,
            price_starting=req.price_starting,
            website_link=req.website_link,
            experience_years=req.experience_years,
            description=req.description,
            image=req.business_image # Transfer the uploaded image
        )
        req.status = 'approved'
        req.save()
        messages.success(request, f'Request approved. Vendor account created! Username: {username}')
        if not req.password:
             messages.info(request, f'Note: A random password was generated: {password}')
    else:
        messages.warning(request, 'Vendor with this name already exists.')
        
    return redirect('superadmin_partners')

@user_passes_test(is_superadmin, login_url='superadmin_login')
def partner_reject(request, pk):
    from apps.website.models import VendorRequest
    req = VendorRequest.objects.get(pk=pk)
    req.status = 'rejected'
    req.save()
    messages.success(request, f'Registration request for "{req.business_name}" rejected.')
    return redirect('superadmin_partners')

@user_passes_test(is_superadmin, login_url='superadmin_login')
def category_add(request):
    from apps.website.models import Category
    from django.utils.text import slugify
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        image = request.FILES.get('image')
        is_popular = request.POST.get('is_popular') == 'on'
        Category.objects.create(name=name, slug=slug, image=image, is_popular=is_popular)
        messages.success(request, 'Category added successfully.')
        return redirect('superadmin_categories')
    return render(request, 'superadmin/category_form.html')

@user_passes_test(is_superadmin, login_url='superadmin_login')
def category_edit(request, pk):
    from apps.website.models import Category
    from django.utils.text import slugify
    category = Category.objects.get(pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug') or slugify(category.name)
        if request.FILES.get('image'):
            category.image = request.FILES.get('image')
        category.is_popular = request.POST.get('is_popular') == 'on'
        category.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('superadmin_categories')
    return render(request, 'superadmin/category_form.html', {'category': category})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def category_delete(request, pk):
    from apps.website.models import Category
    category = Category.objects.get(pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('superadmin_categories')

@user_passes_test(is_superadmin, login_url='superadmin_login')
def vendor_add(request):
    from apps.website.models import Category, Vendor
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        location = request.POST.get('location')
        price_starting = request.POST.get('price_starting', 0)
        description = request.POST.get('description', '')
        is_verified = request.POST.get('is_verified') == 'on'
        is_premium = request.POST.get('is_premium') == 'on'
        image = request.FILES.get('image')
        
        category = Category.objects.get(id=category_id)
        Vendor.objects.create(
            name=name, category=category, location=location, price_starting=price_starting,
            description=description, is_verified=is_verified, is_premium=is_premium, image=image
        )
        messages.success(request, 'Vendor added successfully.')
        return redirect('superadmin_vendors')
    return render(request, 'superadmin/vendor_form.html', {'categories': categories})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def vendor_edit(request, pk):
    from apps.website.models import Category, Vendor
    vendor = Vendor.objects.get(pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        vendor.name = request.POST.get('name')
        category_id = request.POST.get('category')
        vendor.category = Category.objects.get(id=category_id)
        vendor.location = request.POST.get('location')
        vendor.price_starting = request.POST.get('price_starting', 0)
        vendor.description = request.POST.get('description', '')
        vendor.is_verified = request.POST.get('is_verified') == 'on'
        vendor.is_premium = request.POST.get('is_premium') == 'on'
        if request.FILES.get('image'):
            vendor.image = request.FILES.get('image')
        vendor.save()
        messages.success(request, 'Vendor updated successfully.')
        return redirect('superadmin_vendors')
    return render(request, 'superadmin/vendor_form.html', {'vendor': vendor, 'categories': categories})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def vendor_view(request, pk):
    from apps.website.models import Vendor, VendorImage, Review, Inquiry
    vendor = Vendor.objects.get(pk=pk)
    gallery = VendorImage.objects.filter(vendor=vendor)
    reviews = Review.objects.filter(vendor=vendor)
    inquiries = Inquiry.objects.filter(vendor=vendor).order_by('-created_at')
    return render(request, 'superadmin/vendor_detail.html', {'vendor': vendor, 'gallery': gallery, 'reviews': reviews, 'inquiries': inquiries})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def vendor_delete(request, pk):
    from apps.website.models import Vendor
    vendor = Vendor.objects.get(pk=pk)
    vendor.delete()
    messages.success(request, 'Vendor deleted successfully.')
    return redirect('superadmin_vendors')

@user_passes_test(is_superadmin, login_url='superadmin_login')
def wedding_story_add(request):
    from apps.website.models import Vendor, RealWedding
    venues = Vendor.objects.filter(category__slug='venues')
    photographers = Vendor.objects.filter(category__slug='photographers')
    if request.method == 'POST':
        couple_name = request.POST.get('couple_name')
        location = request.POST.get('location')
        date = request.POST.get('date')
        venue_id = request.POST.get('venue')
        photographer_id = request.POST.get('photographer')
        description = request.POST.get('description', '')
        main_image = request.FILES.get('main_image')
        
        venue = Vendor.objects.filter(id=venue_id).first() if venue_id else None
        photographer = Vendor.objects.filter(id=photographer_id).first() if photographer_id else None
        
        RealWedding.objects.create(
            couple_name=couple_name, location=location, date=date,
            venue=venue, photographer=photographer, description=description, main_image=main_image
        )
        messages.success(request, 'Wedding story added successfully.')
        return redirect('superadmin_wedding_stories')
    return render(request, 'superadmin/wedding_story_form.html', {'venues': venues, 'photographers': photographers})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def wedding_story_edit(request, pk):
    from apps.website.models import Vendor, RealWedding
    story = RealWedding.objects.get(pk=pk)
    venues = Vendor.objects.filter(category__slug='venues')
    photographers = Vendor.objects.filter(category__slug='photographers')
    if request.method == 'POST':
        story.couple_name = request.POST.get('couple_name')
        story.location = request.POST.get('location')
        story.date = request.POST.get('date')
        venue_id = request.POST.get('venue')
        photographer_id = request.POST.get('photographer')
        story.venue = Vendor.objects.filter(id=venue_id).first() if venue_id else None
        story.photographer = Vendor.objects.filter(id=photographer_id).first() if photographer_id else None
        story.description = request.POST.get('description', '')
        if request.FILES.get('main_image'):
            story.main_image = request.FILES.get('main_image')
        story.save()
        messages.success(request, 'Wedding story updated successfully.')
        return redirect('superadmin_wedding_stories')
    return render(request, 'superadmin/wedding_story_form.html', {'story': story, 'venues': venues, 'photographers': photographers})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def wedding_story_delete(request, pk):
    from apps.website.models import RealWedding
    story = RealWedding.objects.get(pk=pk)
    story.delete()
    messages.success(request, 'Wedding story deleted successfully.')
    return redirect('superadmin_wedding_stories')


@user_passes_test(is_superadmin, login_url='superadmin_login')
def users_list(request):
    from django.contrib.auth.models import User
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'superadmin/users.html', {'users': users})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def user_toggle(request, pk):
    from django.contrib.auth.models import User
    user = User.objects.get(pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "suspended"
    messages.success(request, f'Customer account {status} successfully.')
    return redirect('superadmin_users')


@user_passes_test(is_superadmin, login_url='superadmin_login')
def reviews_list(request):
    from apps.website.models import Review
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'superadmin/reviews.html', {'reviews': reviews})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def review_delete(request, pk):
    from apps.website.models import Review
    review = Review.objects.get(pk=pk)
    review.delete()
    messages.success(request, 'Review deleted successfully.')
    return redirect('superadmin_reviews')


@user_passes_test(is_superadmin, login_url='superadmin_login')
def inquiries_list(request):
    from apps.website.models import Inquiry
    inquiries = Inquiry.objects.all().order_by('-created_at')
    return render(request, 'superadmin/inquiries.html', {'inquiries': inquiries})

@user_passes_test(is_superadmin, login_url='superadmin_login')
def advanced_settings(request):
    from apps.website.models import SiteSetting
    setting, created = SiteSetting.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        setting.site_title = request.POST.get('site_title', setting.site_title)
        setting.contact_email = request.POST.get('contact_email', setting.contact_email)
        setting.contact_phone = request.POST.get('contact_phone', setting.contact_phone)
        setting.address = request.POST.get('address', setting.address)
        setting.facebook_link = request.POST.get('facebook_link', setting.facebook_link)
        setting.instagram_link = request.POST.get('instagram_link', setting.instagram_link)
        setting.twitter_link = request.POST.get('twitter_link', setting.twitter_link)
        setting.maintenance_mode = 'maintenance_mode' in request.POST
        setting.save()
        messages.success(request, 'Advanced settings updated successfully.')
        return redirect('superadmin_advanced_settings')
        
    return render(request, 'superadmin/advanced_settings.html', {'setting': setting})
