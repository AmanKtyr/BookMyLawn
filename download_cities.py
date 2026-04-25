import urllib.request
import os

# Define the base directory for static images
base_dir = r"d:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\static\website\img\cities"

# Dictionary of city names to high-quality Unsplash URLs
city_images = {
    "mumbai.jpg": "https://images.unsplash.com/photo-1566552881560-0be862a7c445?q=80&w=800&auto=format&fit=crop", 
    "delhi.jpg": "https://images.unsplash.com/photo-1587474260584-136574528ed5?q=80&w=800&auto=format&fit=crop", 
    "bangalore.jpg": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?q=80&w=800&auto=format&fit=crop", 
    "udaipur.jpg": "https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?q=80&w=800&auto=format&fit=crop", 
    "lucknow.jpg": "https://images.unsplash.com/photo-1582653280644-cc6f01487f87?q=80&w=800&auto=format&fit=crop", 
    "jaipur.jpg": "https://images.unsplash.com/photo-1599661046289-e31897846e41?q=80&w=800&auto=format&fit=crop", 
    "goa.jpg": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=800&auto=format&fit=crop", 
    "chandigarh.jpg": "https://images.unsplash.com/photo-1619623223050-8b22a61a067f?q=80&w=800&auto=format&fit=crop", 
}

os.makedirs(base_dir, exist_ok=True)

for filename, url in city_images.items():
    full_path = os.path.join(base_dir, filename)
    if os.path.exists(full_path):
        continue
    print(f"Downloading {url} to {full_path}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(full_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("City images updated successfully!")
