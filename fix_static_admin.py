import os
import re

file_path = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\superadmin\templates\superadmin\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add load static if not present
if '{% load static %}' not in content:
    content = '{% load static %}\n' + content

# Replace standard dirs
for d in ['css', 'js', 'fonts', 'assets', 'data', 'images', 'img']:
    content = re.sub(fr'href="({d}/[^"]+)"', rf'href="{{% static \'superadmin/\1\' %}}"', content)
    content = re.sub(fr'src="({d}/[^"]+)"', rf'src="{{% static \'superadmin/\1\' %}}"', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
