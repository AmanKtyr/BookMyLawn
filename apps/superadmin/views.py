from django.shortcuts import render
from apps.website.models import Vendor, Review

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
