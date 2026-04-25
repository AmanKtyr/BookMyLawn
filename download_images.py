import urllib.request
import os

# Define the base directory for static images
base_dir = r"d:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\static\website\img"

# Dictionary of image paths to replace with specific high-quality Unsplash wedding URLs
# Note: These are direct Unsplash CDN URLs for high-quality, royalty-free images.
images = {
    # Hero Banner
    r"banner\banner-1.jpg": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=2070&auto=format&fit=crop", # Beautiful wedding setup
    
    # Categories
    r"categories\category-1.jpg": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?q=80&w=800&auto=format&fit=crop", # Venue
    r"categories\category-2.jpg": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?q=80&w=800&auto=format&fit=crop", # Photographer
    r"categories\category-3.jpg": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?q=80&w=800&auto=format&fit=crop", # Decorator
    r"categories\category-4.jpg": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?q=80&w=800&auto=format&fit=crop", # Makeup/Bride
    
    # Products / Vendors / Real Weddings
    r"product\product-1.jpg": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?q=80&w=800&auto=format&fit=crop", # Beach Wedding
    r"product\product-2.jpg": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?q=80&w=800&auto=format&fit=crop", # Royal Wedding
    r"product\product-3.jpg": "https://images.unsplash.com/photo-1522673607200-164d1b6ce486?q=80&w=800&auto=format&fit=crop", # Intimate Vows
}

for rel_path, url in images.items():
    full_path = os.path.join(base_dir, rel_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    print(f"Downloading {url} to {full_path}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(full_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded: {rel_path}")
    except Exception as e:
        print(f"Failed to download {rel_path}: {e}")

print("All images updated successfully!")
