import csv, os

def remove_apollo_cols(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = [h for h in reader.fieldnames if h not in ('Enrich Phone via Apollo', 'Enrich via Apollo')]
        rows = [{h: row[h] for h in headers} for row in reader]
    
    with open(input_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f'{os.path.basename(input_path)}: {len(rows)} rows, removed Apollo fields, tags with emerald kept')

remove_apollo_cols(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv')
remove_apollo_cols(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Dispensaries.csv')
