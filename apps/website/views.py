from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Vendor, Category, RealWedding, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem

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
    return render(request, 'website/vendor-details.html', {'vendor': vendor})

def contact(request):
    return render(request, 'website/contact.html')

def real_weddings(request):
    weddings = RealWedding.objects.all().order_by('-date')
    return render(request, 'website/real-weddings.html', {'weddings': weddings})

def login_view(request):
    user_type = request.GET.get('type')
    return render(request, 'website/login.html', {'user_type': user_type})

def register_view(request):
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
        price_starting = request.POST.get('price_starting', 0)
        website_link = request.POST.get('website_link', '')
        experience_years = request.POST.get('experience_years', 0)
        description = request.POST.get('description', '')
        business_image = request.FILES.get('business_image')

        VendorRequest.objects.create(
            business_name=business_name,
            category=category,
            owner_name=owner_name,
            email=email,
            phone=phone,
            city=city,
            price_starting=price_starting,
            website_link=website_link,
            experience_years=experience_years,
            description=description,
            business_image=business_image
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
