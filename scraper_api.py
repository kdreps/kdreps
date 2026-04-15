import json
import re
import urllib.request
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(url, save_path):
    if os.path.exists(save_path):
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

with open("baza.js", "r", encoding="utf-8") as f:
    content = f.read()

# Extract array content
match = re.search(r"const KAKOBUY_DB = \[\s*(.*?)\s*\];", content, flags=re.DOTALL)
if not match:
    print("Could not parse baza.js")
    exit(1)

array_str = match.group(1)
# allow python to parse non-strict JSON if needed, but remove trailing comma
array_str = re.sub(r",\s*$", "", array_str)
valid_json_str = "[" + array_str + "]"

try:
    items = json.loads(valid_json_str)
except Exception as e:
    print("Failed to parse JSON:", e)
    # try manually matching lines if json parse fails
    exit(1)

os.makedirs("assets/weidian", exist_ok=True)

# Prepare download tasks
tasks = []
for item in items:
    img_url = item.get("image", "")
    if img_url.startswith("http"):
        ext = ".jpg"
        if ".png" in img_url: ext = ".png"
        
        md5 = hashlib.md5(img_url.encode('utf-8')).hexdigest()
        local_path = f"assets/weidian/img_{md5[:8]}{ext}"
        
        tasks.append((img_url, local_path, item))

print(f"Found {len(tasks)} items with HTTP images. Downloading...")

downloaded_count = 0
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(download_image, t[0], t[1]): t for t in tasks}
    for future in as_completed(futures):
        t = futures[future]
        success = future.result()
        if success:
            t[2]["image"] = t[1]
            downloaded_count += 1

print(f"Downloaded {downloaded_count} images.")

# Sort items by category
# The user wants products segregated to appropriate sections.
# Sorting them by category will achieve a clean segregation in baza.js
items.sort(key=lambda x: x.get("category", "zz_inne"))

new_content = "const KAKOBUY_DB = [\n"
for item in items:
    # Use json dump to output each item, ensuring formatting is correct and compact
    new_content += f'  {json.dumps(item, ensure_ascii=False)},\n'
new_content += "];\n"

with open("baza.js", "w", encoding="utf-8") as f:
    f.write(new_content)

print("baza.js successfully sorted by category and updated with local asset paths.")
