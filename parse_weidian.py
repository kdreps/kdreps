"""
Parse gviz_data.json to extract product names + links,
then match them to baza.js entries by name and update links.
"""
import json, re, difflib

# Load the gviz data
with open('gviz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = data.get('table', {}).get('rows', [])
cols = data.get('table', {}).get('cols', [])

print(f"Total rows: {len(rows)}, cols: {len(cols)}")

# Extract all (name, link) pairs from the spreadsheet
# Structure: multiple product sections side by side
# Col 2=shoe name, Col 6=shoe link
# Col 16=bluza name, Col 21=bluza link  (0-indexed)
# Col 30=perfumy name, Col 33=perfumy link
# Images col 15, col 29 etc.

# Let's first see what the gviz column mapping looks like
# and scan all rows for cells that have ikako.vip links

sheet_products = []  # list of {name, link, image}

def get_cell(row, idx):
    cells = row.get('c', [])
    if idx < len(cells) and cells[idx]:
        return cells[idx].get('v') or cells[idx].get('f')
    return None

def get_link_from_cell(row, idx):
    """gviz stores hyperlinks in the 'p' property or in formatted value"""
    cells = row.get('c', [])
    if idx < len(cells) and cells[idx]:
        cell = cells[idx]
        # Check for hyperlink in properties
        f = cell.get('f', '')  # formatted value
        v = cell.get('v', '')  # value
        p = cell.get('p', {})  # custom properties
        
        if f and ('ikako' in str(f) or 'kakobuy' in str(f) or 'weidian' in str(f)):
            return str(f)
        if v and ('ikako' in str(v) or 'kakobuy' in str(v) or 'weidian' in str(v)):
            return str(v)
        if p:
            for key, val in p.items():
                if isinstance(val, str) and ('ikako' in val or 'kakobuy' in val):
                    return val
    return None

# Scan ALL cells in all rows looking for links
all_links = []
for row_idx, row in enumerate(rows):
    cells = row.get('c', [])
    for col_idx, cell in enumerate(cells):
        if cell:
            f = str(cell.get('f', '') or '')
            v = str(cell.get('v', '') or '')
            p = cell.get('p', {}) or {}
            
            for val in [f, v] + list(p.values() if isinstance(p, dict) else []):
                val = str(val)
                if 'ikako.vip' in val or ('kakobuy.com' in val and 'affcode' in val):
                    all_links.append({'row': row_idx, 'col': col_idx, 'link': val, 'f': f, 'v': v})

print(f"Found {len(all_links)} links with ikako.vip/kakobuy")
for l in all_links[:5]:
    print(l)

# Also check if links appear in column values as text starting with http
text_links = []
for row_idx, row in enumerate(rows):
    cells = row.get('c', [])
    for col_idx, cell in enumerate(cells):
        if cell:
            v = str(cell.get('v', '') or '')
            if v.startswith('http') and ('ikako' in v or 'kakobuy' in v or 'weidian' in v):
                text_links.append({'row': row_idx, 'col': col_idx, 'url': v})

print(f"\nFound {len(text_links)} URL text values")
for l in text_links[:5]:
    print(l)

# Check a few rows around row 22-25 (data starts at row ~22 in 0-based gviz)
print("\n--- Sample rows 20-24 (all non-null cells) ---")
for row_idx in range(20, 26):
    if row_idx < len(rows):
        row = rows[row_idx]
        cells = row.get('c', [])
        non_null = []
        for i, c in enumerate(cells):
            if c and (c.get('v') is not None or c.get('f')):
                non_null.append((i, {'v': c.get('v'), 'f': c.get('f'), 'p': c.get('p')}))
        if non_null:
            print(f"Row {row_idx}: {non_null[:10]}")
