with open('kdreps.html', 'r', encoding='utf-8') as f:
    html = f.read()

categories_titles = [
    'koszulki-pilkarskie',
    'spodenki',
    'spodnie',
    'buty',
    'sety',
    'skarpetki',
    'majtki',
    'paski',
    'portfele',
    'plecaki',
    'czapki',
    'kurtki',
    'perfumy',
    'linki' # 'linki' is the page after perfumy
]

for cat_id in categories_titles:
    html = html.replace(f'<div class="page" id="page-{cat_id}">', f'</div>\n<div class="page" id="page-{cat_id}">')

with open('kdreps.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed kdreps.html closing tag problem")
