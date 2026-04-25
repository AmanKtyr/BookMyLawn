import os
import glob

apps_dir = r'd:\Work-Space\Industrial Prijects\BookMyLawn\apps'

html_files = glob.glob(os.path.join(apps_dir, '**/*.html'), recursive=True)

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "\\'" in content:
        new_content = content.replace("\\'", "'")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed quotes in {os.path.basename(file_path)}")
