import os
import re

file_path = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\templates\website\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add load static if not present
if '{% load static %}' not in content:
    content = '{% load static %}\n' + content

# Replace css/
content = re.sub(r'href="(css/[^"]+)"', r'href="{% static \'website/\1\' %}"', content)
# Replace js/
content = re.sub(r'src="(js/[^"]+)"', r'src="{% static \'website/\1\' %}"', content)
# Replace img/
content = re.sub(r'src="(img/[^"]+)"', r'src="{% static \'website/\1\' %}"', content)
# Replace background images
content = re.sub(r'data-setbg="(img/[^"]+)"', r'data-setbg="{% static \'website/\1\' %}"', content)
content = re.sub(r"url\('img/([^']+)'\)", r"url('{% static \'website/img/\1\' %}')", content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
