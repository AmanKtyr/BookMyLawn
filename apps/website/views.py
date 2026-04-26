from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Vendor, Category, RealWedding

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
        
    return render(request, 'website/vendors.html', {'vendors': all_vendors, 'categories': categories, 'view_type': view_type})

def vendor_details(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    return render(request, 'website/vendor-details.html', {'vendor': vendor})

def contact(request):
    return render(request, 'website/contact.html')

def real_weddings(request):
    weddings = RealWedding.objects.all().order_by('-date')
    return render(request, 'website/real-weddings.html', {'weddings': weddings})

def login_view(request):
    return render(request, 'website/login.html')

def register_view(request):
    return render(request, 'website/register.html')

def vendor_register_view(request):
    return render(request, 'website/vendor-register.html')
