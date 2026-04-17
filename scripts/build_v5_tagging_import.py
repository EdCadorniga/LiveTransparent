import pandas as pd
import csv
from pathlib import Path

# Clean snake_case mapping as requested
TAG_MAPPING = {
    'MSO Executive': 'mso_executive',
    'MSO Finance': 'mso_finance',
    'MSO Marketing': 'mso_marketing',
    'MSO Retail & Sales': 'mso_retail_sales',
    'SSO Executive': 'sso_executive',
    'SSO Finance': 'sso_finance',
    'SSO Marketing': 'sso_marketing',
    'SSO Retail & Sales': 'sso_retail_sales',
    'DO NOT CONTACT': 'Do Not Contact',
    'DO NOT CONTACT ': 'Do Not Contact'
}

def clean(value):
    return str(value).strip() if pd.notna(value) else ''

def main():
    file_path = 'Contact List.v5.xlsx'
    print(f"Reading {file_path}...")
    
    # Read the Masterlist sheet
    df = pd.read_excel(file_path, sheet_name='Masterlist', header=1)
    
    # Filter for rows that MUST have an Email AND have an Ed Mapping
    df = df[df['Primary Email'].notna() & df['Ed Mapping'].notna()]
    
    output_rows = []
    for _, row in df.iterrows():
        email = clean(row.get('Primary Email'))
        mapping_val = clean(row.get('Ed Mapping'))
        
        tag = TAG_MAPPING.get(mapping_val)
        if not tag:
            tag = TAG_MAPPING.get(mapping_val.strip())
            
        if tag:
            output_rows.append({
                'Email': email,
                'First Name': clean(row.get('First Name')),
                'Last Name': clean(row.get('Last Name')),
                'Tags': tag
            })

    output_file = 'ghl_v5_tagging_import_email_only.csv'
    print(f"Writing {len(output_rows)} rows to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Email', 'First Name', 'Last Name', 'Tags'])
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Done! Created {output_file}")

if __name__ == "__main__":
    main()
