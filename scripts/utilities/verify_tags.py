import csv
for fname in ['GHL_Ready_Brands.csv', 'GHL_Ready_Dispensaries.csv']:
    path = r'C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\\' + fname
    with open(path) as f:
        reader = csv.DictReader(f)
        row = next(reader)
        t = row.get('Tags', '')
        e = row.get('Enrich Phone via Apollo', '')
        print(f'{fname}: Tags={t!r}, Enrich={e!r}')
        for r in reader:
            if not r.get('Phone', '').strip():
                print(f'  No-phone: Tags={r["Tags"]!r}, Enrich={r["Enrich Phone via Apollo"]!r}')
                break
