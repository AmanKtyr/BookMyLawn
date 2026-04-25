import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.website.models import Category, Vendor, Review

def seed_db():
    print("Clearing existing data...")
    Review.objects.all().delete()
    Vendor.objects.all().delete()
    Category.objects.all().delete()

    print("Creating categories...")
    venues = Category.objects.create(name='Venues', slug='venues')
    photo = Category.objects.create(name='Photographers', slug='photographers')
    decor = Category.objects.create(name='Decorators', slug='decorators')

    print("Creating vendors...")
    v1 = Vendor.objects.create(
        name='The Grand Lawn & Banquet',
        category=venues,
        location='Mumbai',
        price_starting=150000,
        description='The Grand Lawn & Banquet is a premium destination for luxury weddings. With over 2 acres of lush green lawns and a magnificent air-conditioned banquet hall, it can host up to 1000 guests seamlessly.',
        is_premium=True,
        is_verified=True
    )
    v2 = Vendor.objects.create(
        name='Focus Photography Studio',
        category=photo,
        location='Delhi',
        price_starting=80000,
        description='We capture the magic of your special day. Our expert photographers specialize in candid and traditional wedding photography.',
        is_premium=False,
        is_verified=True
    )
    v3 = Vendor.objects.create(
        name='Elegant Event Decorators',
        category=decor,
        location='Bangalore',
        price_starting=120000,
        description='Transforming spaces into magical wedding venues. We offer bespoke floral and thematic decorations.',
        is_premium=False,
        is_verified=False
    )

    print("Creating reviews...")
    Review.objects.create(vendor=v1, reviewer_name='Rahul & Sneha', rating=5, comment='Absolutely stunning venue! The management was incredibly helpful and our guests couldn\'t stop praising the food. Highly recommended!')
    Review.objects.create(vendor=v1, reviewer_name='Priya Sharma', rating=4, comment='Beautiful decor and ample parking space. Only issue was slightly slow service at the live counters, but overall a magical experience.')
    Review.objects.create(vendor=v2, reviewer_name='Ankit T.', rating=5, comment='Best photography team in Delhi!')

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_db()
