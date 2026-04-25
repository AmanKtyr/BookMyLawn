import os

file_path = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\templates\website\index.html'
base_path = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps\website\templates\website\base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

header_end = '<!-- Header Section End -->'
footer_begin = '<!-- Instagram Begin -->'

if header_end in content and footer_begin in content:
    header_part = content.split(header_end)[0] + header_end + '\n'
    middle_part = content.split(header_end)[1].split(footer_begin)[0]
    footer_part = footer_begin + content.split(header_end)[1].split(footer_begin)[1]
    
    base_content = header_part + '\n{% block content %}\n{% endblock %}\n\n' + footer_part
    
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
        
    index_content = "{% extends 'website/base.html' %}\n{% load static %}\n\n{% block content %}\n" + middle_part + "\n{% endblock %}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("Templates converted successfully.")
else:
    print("Could not find delimiters.")
