import csv, os

def add_columns(input_path, output_path):
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames[:]
        new_cols = ['Enrich Phone via Apollo', 'Enrich via Apollo']
        new_headers = headers + new_cols
        
        for row in reader:
            needs_enrich = not row.get('Phone', '') or row['Phone'].strip() == ''
            row['Enrich Phone via Apollo'] = 'Yes' if needs_enrich else ''
            row['Enrich via Apollo'] = 'Yes' if needs_enrich else ''
            current_tags = row.get('Tags', '')
            if current_tags and 'emerald' not in current_tags:
                row['Tags'] = current_tags + ',emerald'
            rows.append(row)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_headers)
        writer.writeheader()
        writer.writerows(rows)
    
    enrich_count = sum(1 for r in rows if r['Enrich Phone via Apollo'] == 'Yes')
    print(f'{os.path.basename(output_path)}: {len(rows)} rows, {enrich_count} flagged for Apollo enrichment')

add_columns(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv', r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Brands.csv')
add_columns(r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Dispensaries.csv', r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\GHL_Ready_Dispensaries.csv')
