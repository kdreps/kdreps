import requests, json, re

session = requests.Session()

# Published HTML of the sheet - preserves hyperlinks
r = session.get(
    'https://docs.google.com/spreadsheets/d/1qiFevU2X5OvO-rtM5ZlBhM893abQwP0USRnYLFYTBcA/pubhtml',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)
print('Status:', r.status_code, 'Size:', len(r.content))

content = r.text

# Save full HTML for inspection
with open('pubhtml.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Find all hyperlinks
links = re.findall(r'href=["\'](https?://[^"\']+)["\']', content)
ikako_links = [l for l in links if 'ikako.vip' in l or 'kakobuy' in l]
print('ikako/kakobuy links found:', len(ikako_links))
for l in ikako_links[:5]:
    print(l)

with open('pubhtml_links.json', 'w', encoding='utf-8') as f:
    json.dump({'total': len(ikako_links), 'links': ikako_links}, f, ensure_ascii=False, indent=2)

print('Done')
