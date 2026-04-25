import urllib.request
import os

# Define the base directory for static images
base_dir = r"d:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\static\website\img\cities"

# Dictionary of city names to high-quality Unsplash URLs
city_images = {
    "lucknow.jpg": "https://images.unsplash.com/photo-1583000571991-3291580cae79?q=80&w=800&auto=format&fit=crop", 
    "chandigarh.jpg": "https://images.unsplash.com/photo-1629126487040-3573a492f23b?q=80&w=800&auto=format&fit=crop", 
}

os.makedirs(base_dir, exist_ok=True)

for filename, url in city_images.items():
    full_path = os.path.join(base_dir, filename)
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
