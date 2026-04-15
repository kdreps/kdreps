import json
import re

def get_category(name):
    n = name.lower()
    if any(x in n for x in ['hat', 'cap', 'beanie', 'czapka', 'hood', '棉帽', '帽子']):
        return 'czapki'
    if any(x in n for x in ['shoe', 'sneaker', 'buty', 'jordan', 'dunk', 'yeezy', 'af1']):
        return 'buty'
    if any(x in n for x in ['jacket', 'coat', 'kurtka', 'vest']):
        return 'kurtki'
    if any(x in n for x in ['short', 'spodenki']):
        return 'spodenki'
    if any(x in n for x in ['pant', 'jean', 'trouser', 'spodnie', 'dresy', '卫裤']):
        return 'spodnie'
    if any(x in n for x in ['t-shirt', 'shirt', 'hoodie', 'sweatshirt', 'polo', 'sweater', 'sweter', 'koszulka', 'bluza', '卫衣', 't恤']):
        return 'koszulki-bluzy'
    if any(x in n for x in ['pack', 'bag', 'plecak', 'nerka', '书包', '背包']):
        return 'plecaki'
    if any(x in n for x in ['perfum']):
        return 'perfumy'
    if any(x in n for x in ['belt', 'pasek']):
        return 'paski'
    if any(x in n for x in ['wallet', 'portfel']):
        return 'portfele'
    if any(x in n for x in ['sock', 'skarpetki']):
        return 'skarpetki'
    if any(x in n for x in ['underwear', 'majtki']):
        return 'majtki'
    # Default
    return 'koszulki-bluzy' # safe fallback

# Read Weidian items
with open("weidian_raw_data.json", "r", encoding="utf-8") as f:
    weidian_items = json.load(f)

# Read existing baza.js
with open("baza.js", "r", encoding="utf-8") as f:
    baza_lines = f.readlines()

existing_links = set()
for line in baza_lines:
    if '"link":' in line:
        match = re.search(r'"link":\s*"([^"]+)"', line)
        if match:
            link = match.group(1)
            if link != "#" and link != "":
                existing_links.add(link)

new_lines_to_add = []
added_count = 0
for item in weidian_items:
    url = item.get("itemUrl", "")
    if url in existing_links:
        continue # skip duplicate
        
    name = item.get("itemName", "Unknown")
    price_cny = item.get("price", "0")
    try:
        price_pln = f"{float(price_cny) * 0.546:.2f}"
    except:
        price_pln = "0.00"
    
    img = item.get("itemImg", "")
    cat = get_category(name)
    
    # Format entry
    name_clean = name.replace('"', '\\"')
    entry = f'  {{"category": "{cat}", "name": "{name_clean}", "pricePLN": "{price_pln}", "priceCNY": "{price_cny}", "quality": "TOP", "link": "{url}", "image": "{img}"}},\n'
    new_lines_to_add.append(entry)
    existing_links.add(url)
    added_count += 1

if added_count == 0:
    print("No new items to add (all duplicates).")
else:
    # Find insertion point: right before ];
    insert_idx = -1
    for i in range(len(baza_lines)-1, -1, -1):
        if "];" in baza_lines[i]:
            insert_idx = i
            break
            
    if insert_idx != -1:
        # Check if the line before insertion has a comma, if not, we probably should add one if it's an object
        if insert_idx > 0 and '}' in baza_lines[insert_idx-1] and not baza_lines[insert_idx-1].strip().endswith(','):
            baza_lines[insert_idx-1] = baza_lines[insert_idx-1].rstrip() + ',\n'
            
        baza_lines = baza_lines[:insert_idx] + new_lines_to_add + baza_lines[insert_idx:]
        
        with open("baza.js", "w", encoding="utf-8") as f:
            f.writelines(baza_lines)
        print(f"Successfully added {added_count} items to baza.js")
    else:
        print("Could not find ]; in baza.js")
