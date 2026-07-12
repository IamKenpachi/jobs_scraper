import re

files = ['targetjobs_scraper.py', 'jooble_scraper.py', 'reed_scraper.py']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('        os.makedirs', '    os.makedirs')
    content = content.replace('        timestamp =', '    timestamp =')
    content = content.replace('        filename =', '    filename =')
    content = content.replace('        df.to_csv', '    df.to_csv')
    content = content.replace('        print(f"Saved final data', '    print(f"Saved final data')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
