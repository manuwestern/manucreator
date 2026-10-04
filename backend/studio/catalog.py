from pathlib import Path

ASSET_DIR = Path(__file__).parent / 'assets'
FONT_FILES = {'modern': 'modern.otf', 'classic': 'classic.otf', 'bold': 'bold.otf', 'sans': 'LiberationSans-Regular.ttf', 'sans-bold': 'LiberationSans-Bold.ttf', 'sans-italic': 'LiberationSans-Italic.ttf', 'serif': 'LiberationSerif-Regular.ttf', 'serif-italic': 'LiberationSerif-Italic.ttf', 'mono': 'LiberationMono-Regular.ttf', 'narrow': 'LiberationSansNarrow-Regular.ttf'}
PRODUCTS = [
    {'id': 'holzscheibe', 'name': 'Holzscheibe', 'subtitle': 'Natürlich. Persönlich. Einzigartig.', 'material': 'Birkenholz', 'category': 'holz', 'price_cents': 2490, 'dimensions': 'Ø 220 × 15 mm', 'area_mm': '100 × 105 mm', 'max_text': 28, 'area': {'x': 250, 'y': 255, 'w': 300, 'h': 290}, 'ink': '#493627', 'templates': ['text', 'photo', 'logo']},
    {'id': 'schneidebrett', 'name': 'Schneidebrett', 'subtitle': 'Ein Lieblingsstück für jeden Tag.', 'material': 'Eichenholz', 'category': 'holz', 'price_cents': 3490, 'dimensions': '240 × 340 × 18 mm', 'area_mm': '120 × 150 mm', 'max_text': 30, 'area': {'x': 270, 'y': 250, 'w': 260, 'h': 320}, 'ink': '#493627', 'templates': ['text', 'photo', 'logo']},
    {'id': 'glasschild', 'name': 'Glasschild', 'subtitle': 'Klare Formen. Deine Botschaft.', 'material': 'Klarglas', 'category': 'glas', 'price_cents': 2990, 'dimensions': '240 × 160 × 6 mm', 'area_mm': '150 × 75 mm', 'max_text': 30, 'area': {'x': 235, 'y': 315, 'w': 330, 'h': 170}, 'ink': '#53605d', 'templates': ['text', 'logo']},
    {'id': 'metallanhaenger', 'name': 'Metallanhänger', 'subtitle': 'Kleine Details, die bleiben.', 'material': 'Edelstahl', 'category': 'metall', 'price_cents': 1490, 'dimensions': 'Ø 40 × 2 mm', 'area_mm': '25 × 22 mm', 'max_text': 18, 'area': {'x': 275, 'y': 310, 'w': 250, 'h': 230}, 'ink': '#333b3a', 'templates': ['text', 'logo']},
]
BY_ID = {p['id']: p for p in PRODUCTS}

def public_products():
    return [{**p, 'image': f"/images/studio/{p['id']}.webp", 'is_sample': True, 'production_approved': False} for p in PRODUCTS]