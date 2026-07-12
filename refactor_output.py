import os

files = [
    'targetjobs_scraper.py',
    'jooble_scraper.py',
    'reed_scraper.py',
    'milkround_scraper.py',
    'cwjobs_scraper.py',
    'totaljobs_scraper.py'
]

replacement_logic = """
        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"output/{site_name}_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved final data to {filename}.")"""

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    site_name = f.split('_')[0]
    
    # Add imports if they don't exist
    if 'from datetime import datetime' not in content:
        content = "import os\nfrom datetime import datetime\n" + content
        
    # Replace the exact to_csv line based on how we wrote it
    if f == 'targetjobs_scraper.py':
        content = content.replace('df.to_csv("targetjobs_data.csv", index=False)\n    print("Saved targetjobs_data.csv!")', replacement_logic.replace('{site_name}', site_name).strip())
    elif f == 'jooble_scraper.py':
        content = content.replace('df.to_csv("jooble_data.csv", index=False)\n    print("Saved Jooble data to jooble_data.csv.")', replacement_logic.replace('{site_name}', site_name).strip())
    elif f == 'reed_scraper.py':
        content = content.replace('df.to_csv("reed_data.csv", index=False)\n    print("Saved Reed API data to reed_data.csv.")', replacement_logic.replace('{site_name}', site_name).strip())
    elif f == 'milkround_scraper.py':
        content = content.replace('df.to_csv("milkround_data.csv", index=False)\n        print("Saved final data to milkround_data.csv.")', replacement_logic.replace('{site_name}', site_name).strip())
    elif f == 'cwjobs_scraper.py':
        content = content.replace('df.to_csv("cwjobs_data.csv", index=False)\n        print("Saved final data to cwjobs_data.csv.")', replacement_logic.replace('{site_name}', site_name).strip())
    elif f == 'totaljobs_scraper.py':
        content = content.replace('df.to_csv("totaljobs_data.csv", index=False)\n        print("Saved final data to totaljobs_data.csv.")', replacement_logic.replace('{site_name}', site_name).strip())

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
