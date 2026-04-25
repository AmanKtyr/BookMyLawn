import os
import glob

template_dir = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\templates\website'
base_path = os.path.join(template_dir, 'base.html')

header_end = '<!-- Header Section End -->'
footer_begin = '<!-- Instagram Begin -->'
if not os.path.exists(base_path):
    print("base.html not found, cannot convert.")
    exit(1)

html_files = glob.glob(os.path.join(template_dir, '*.html'))
for file_path in html_files:
    if os.path.basename(file_path) in ['index.html', 'base.html', 'main.html']:
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if header_end in content and footer_begin in content:
        middle_part = content.split(header_end)[1].split(footer_begin)[0]
        
        new_content = "{% extends 'website/base.html' %}\n{% load static %}\n\n{% block content %}\n" + middle_part + "\n{% endblock %}\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Converted {os.path.basename(file_path)}")
    else:
        print(f"Skipping {os.path.basename(file_path)}: delimiters not found.")
