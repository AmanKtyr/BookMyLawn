from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_popular = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
        
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_profile')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vendors')
    location = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    price_starting = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Specifics for Venues
    veg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    non_veg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    capacity = models.IntegerField(default=0)
    rooms = models.IntegerField(default=0)
    
    # Details
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text="Comma separated values: AC, Parking, etc.")
    map_link = models.URLField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    image = models.ImageField(upload_to='vendors/', null=True, blank=True)
    website_link = models.URLField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def amenities_list(self):
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(',') if a.strip()]
    
    def __str__(self):
        return self.name

class VendorImage(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='vendor_gallery/')
    caption = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery for {self.vendor.name}"

class VendorRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100) # Simple charfield for form submission
    owner_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    price_starting = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    website_link = models.URLField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    business_image = models.ImageField(upload_to='vendor_requests/', null=True, blank=True)
    description = models.TextField(blank=True)
    password = models.CharField(max_length=128, null=True, blank=True) # Desired password for the account
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.business_name} ({self.status})"

class Review(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.reviewer_name} - {self.vendor.name} ({self.rating}/5)"

class RealWedding(models.Model):
    couple_name = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    venue = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='weddings_at_venue')
    photographer = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='weddings_shot')
    date = models.DateField()
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='real_weddings/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.couple_name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    event_date = models.DateField()
    location = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} in Cart {self.cart.id}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    event_date = models.DateField()
    location = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vendor.name} in Order {self.order.id}"

class Inquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='inquiries')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    event_date = models.DateField(null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('new', 'New'), ('contacted', 'Contacted'), ('closed', 'Closed')], default='new')

    def __str__(self):
        return f"Inquiry for {self.vendor.name} by {self.customer_name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True)
    wedding_date = models.DateField(null=True, blank=True)
    partner_name = models.CharField(max_length=150, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class WeddingChecklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checklist_items')
    task_name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.task_name

class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    content = models.TextField()
    author = models.CharField(max_length=100, default='Admin')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class SiteSetting(models.Model):
    site_title = models.CharField(max_length=200, default='BookMyLawn')
    contact_email = models.EmailField(default='support@bookmylawn.com')
    contact_phone = models.CharField(max_length=20, default='+91 00000 00000')
    address = models.TextField(blank=True)
    maintenance_mode = models.BooleanField(default=False)
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global Site Settings"

