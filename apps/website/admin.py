from django.contrib import admin
from .models import Category, Vendor, Review, BlogPost, UserProfile, WeddingChecklist, RealWedding, VendorRequest, SupportTicket

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'price_starting', 'is_verified', 'is_premium')
    list_filter = ('is_verified', 'is_premium', 'category')
    search_fields = ('name', 'location', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_name', 'vendor', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer_name', 'comment')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'created_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'partner_name', 'wedding_date')

@admin.register(WeddingChecklist)
class WeddingChecklistAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_name', 'is_completed', 'due_date')

@admin.register(RealWedding)
class RealWeddingAdmin(admin.ModelAdmin):
    list_display = ('couple_name', 'location', 'date')

@admin.register(VendorRequest)
class VendorRequestAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'owner_name', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'subject', 'status', 'has_attachment', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('vendor__name', 'message', 'admin_reply')
    readonly_fields = ('created_at', 'updated_at')

    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
