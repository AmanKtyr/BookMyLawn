import os
import glob

template_dir = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\superadmin\templates\superadmin'
base_path = os.path.join(template_dir, 'base.html')

main_start = '<main role="main" class="main-content">'
main_end = '</main>'

html_files = glob.glob(os.path.join(template_dir, '*.html'))

# First extract base.html from index.html
index_file = os.path.join(template_dir, 'index.html')
with open(index_file, 'r', encoding='utf-8') as f:
    content = f.read()

if main_start in content and main_end in content:
    header_part = content.split(main_start)[0] + main_start
    middle_part = content.split(main_start)[1].split(main_end)[0]
    footer_part = main_end + content.split(main_start)[1].split(main_end)[1]
    
    base_content = header_part + '\n{% block content %}\n{% endblock %}\n' + footer_part
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
        
    index_content = "{% extends 'superadmin/base.html' %}\n{% load static %}\n\n{% block content %}\n" + middle_part + "\n{% endblock %}\n"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("Extracted base.html from index.html")
        
    # Convert all others
    for file_path in html_files:
        if os.path.basename(file_path) in ['index.html', 'base.html']:
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if main_start in content and main_end in content:
            middle_part = content.split(main_start)[1].split(main_end)[0]
            new_content = "{% extends 'superadmin/base.html' %}\n{% load static %}\n\n{% block content %}\n" + middle_part + "\n{% endblock %}\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Converted {os.path.basename(file_path)}")
        else:
            print(f"Skipping {os.path.basename(file_path)}")
else:
    print("main_start or main_end not found in index.html")
