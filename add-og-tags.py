"""
HoodTip — Add OG tags + Google Maps buttons to all HTML files
Run this from inside your local repo folder:

    python3 add-og-tags.py

- Adds OG/social meta tags to every HTML file missing them
- Adds a Google Maps button to every tip page missing one
- Files already updated are left untouched
"""

import os
import re

BASE_URL = "https://hoodtip.com"

# ── OG DATA ──────────────────────────────────────────────────────────────────
OVERRIDES = {
    "index.html": {
        "title": "HoodTip — Only the good stuff",
        "desc": "Neighbourhood tips from people who actually know. Specific, positive, useful. Geneva, London, Istanbul and beyond.",
        "image": "baindespaquis-sunset.jpg",
    },
    "geneva.html": {
        "title": "Geneva — HoodTip city guide",
        "desc": "The best of Geneva by neighbourhood. Carouge, Plainpalais, Pâquis, Eaux-Vives and beyond.",
        "image": "geneva-hero.jpg",
    },
    "istanbul.html": {
        "title": "Istanbul — HoodTip city guide",
        "desc": "Yeniköy, the Bosphorus, raki-balık, roastery cafés. Istanbul tips from people who know it.",
        "image": "istanbul-hero.jpg",
    },
    "london.html": {
        "title": "London — HoodTip city guide",
        "desc": "Notting Hill, Hampstead, the Electric Cinema, best challah in the city.",
        "image": "london-hero.jpg",
    },
    "carouge.html": {
        "title": "Carouge — Geneva's best neighbourhood · HoodTip",
        "desc": "Saturday market with a violinist, natural wine, oysters at noon.",
        "image": "carouge-cover.jpg",
    },
    "plainpalais.html": {
        "title": "Plainpalais — Geneva · HoodTip",
        "desc": "Bongo Joe on the Rhône, the best takeout sushi in the city, Victoria Hall.",
        "image": "plainpalais-hero-3.jpg",
    },
    "saint-gervais.html": {
        "title": "Saint-Gervais — Geneva · HoodTip",
        "desc": "The Manor food hall, Mulligans for a proper pint, En Faim for lunch.",
        "image": "saintgervais-hero-3.jpg",
    },
    "paquis.html": {
        "title": "Pâquis — Geneva · HoodTip",
        "desc": "Nagomi for the best sushi in Geneva. Bains des Pâquis for a cold swim and rosé on the jetty.",
        "image": "paquis-hero-2.jpg",
    },
    "eaux-vives.html": {
        "title": "Eaux-Vives — Geneva · HoodTip",
        "desc": "Café Chou, Galerie 1 2 3 for vintage Swiss posters, and the lake nearby.",
        "image": "eauxvives-streetscene.jpg",
    },
    "nations.html": {
        "title": "Nations — Geneva · HoodTip",
        "desc": "The beating heart of international Geneva. Shockingly few places to eat. Here are the ones worth knowing.",
        "image": "Nations-chair.jpg",
    },
    "cornavin.html": {
        "title": "Cornavin — Geneva · HoodTip",
        "desc": "Geneva's main station. The Swiss intercity restaurant car: white tablecloth, Alps out the window at 200km/h.",
        "image": "cornavin-station-1.jpg",
    },
    "notting-hill.html": {
        "title": "Notting Hill — London · HoodTip",
        "desc": "The Electric Cinema, The Cow, pastel houses on Portobello Road.",
        "image": "IMG_6278.JPG",
    },
    "yenikoy.html": {
        "title": "Yeniköy — Istanbul · HoodTip",
        "desc": "Raki-balık on the Bosphorus, a roastery café with cats, a bar you won't want to leave.",
        "image": "photo-arnavutkoy-restaurant.jpg",
    },
    "profile-dave.html": {
        "title": "Dave — 49 tips across 7 cities · HoodTip",
        "desc": "Natural wine, proper pubs, waterfront bars, good fish, Saturday markets. Geneva-based.",
        "image": "bongojoe-rhone-light.jpg",
    },
    "profile-paddy.html": {
        "title": "Patrick Eisenstein — HoodTip contributor",
        "desc": "Spends more time looking at watch movements than is strictly healthy. 1 tip in Geneva.",
        "image": "nomos-6.jpg",
    },
    "profile-build.html": {
        "title": "Build your HoodTip profile — share the good stuff",
        "desc": "Not a follower count. Not a star rating. Just the places you actually know.",
        "image": "baindespaquis-sunset.jpg",
    },
    "tip-bongojoe.html": {
        "title": "Bongo Joe — A record shop that became Geneva's best outdoor bar",
        "desc": "Sit on the Rhône, order the local white, ask for the nuts.",
        "image": "bongojoe-yellow-table.jpg",
    },
    "tip-nagomi.html": {
        "title": "Nagomi — The best sushi in Geneva. You are briefly in Tokyo.",
        "desc": "Sit at the bar, order the uni, drink cold sake.",
        "image": "nagomi-chef.jpg",
    },
    "tip-labarge.html": {
        "title": "La Barge — Jump in the Rhône, drink a cold beer, repeat",
        "desc": "A little summer bar right on the water. The best spot in Geneva for submerging your body in cold, fast, clean water.",
        "image": "barge-water-example.jpg",
    },
    "tip-baindespaquis.html": {
        "title": "Bains des Pâquis — 70s vibes on Lac Léman",
        "desc": "Cold rosé on the jetty, jump off the board, Alps right there. Geneva institution since 1932.",
        "image": "baindespaquis-sunset.jpg",
    },
    "tip-tanuki.html": {
        "title": "Tanuki — Really good sushi. Homemade wasabi. Takeout only.",
        "desc": "An elderly Japanese couple, homemade wasabi, a large platter for CHF 110.",
        "image": "tanuki-on-table.jpg",
    },
    "tip-jlc.html": {
        "title": "Jaeger-LeCoultre — The luxury watch you can actually buy in Geneva",
        "desc": "Walk in, buy a watch, leave with it. The watchmaker's watchmaker.",
        "image": "jlc_river.jpg",
    },
    "tip-paulhenri.html": {
        "title": "Paul-Henri Soler — The best wine at the Carouge Saturday market",
        "desc": "CHF 17. Free tastings. Get there before noon.",
        "image": "carouge-wine-bottles.jpg",
    },
    "tip-saintamour.html": {
        "title": "Domaine Saint-Amour — Honour system rosé in a UNESCO vineyard",
        "desc": "Leave money in the box, take a bottle of rosé, sit in the vines above Lake Geneva.",
        "image": "saintamour-lavaux-lake.jpg",
    },
    "tip-belvedere.html": {
        "title": "Grand Hotel Belvedere — Stay here for most of your meals in Wengen",
        "desc": "The sommelier is doing incredible wines. The chef is making some of the best food in the country.",
        "image": "wengen-belvedere-pool-snow.jpg",
    },
    "tip-arnavutkoy.html": {
        "title": "Arnavutköy Restaurant — Raki-balık on the Bosphorus",
        "desc": "Sit outside, order the salad first, drink raki slowly.",
        "image": "photo-arnavutkoy-restaurant.jpg",
    },
    "tip-pero.html": {
        "title": "Pero — Arrive for one drink. Leave hours later.",
        "desc": "A bar in Yeniköy on the Bosphorus. Go.",
        "image": "IMG_7505.JPG",
    },
    "tip-grea.html": {
        "title": "Grea Coffee Nations — Roastery café in Yeniköy with a courtyard and cats",
        "desc": "They roast on site and supply half of Istanbul's better cafés.",
        "image": "photo-roastery-cafe.jpg",
    },
    "tip-iskender.html": {
        "title": "Bursa İskenderoğlu — The İskender kebab. Go here. Get this.",
        "desc": "Lamb over bread, under butter and tomato sauce, yogurt on the side.",
        "image": "Iskender-Bursa.jpg",
    },
    "tip-karmabread.html": {
        "title": "Karma Bread — Best challah in London. Come on Friday.",
        "desc": "That's when they bake it and it goes fast.",
        "image": "london-karmabread-challah-hand.jpg",
    },
    "tip-electriccinema.html": {
        "title": "Electric Cinema — Britain's oldest cinema, still the best one to sit in",
        "desc": "Leather sofa seats, a lamp on your armrest, a glass of champagne.",
        "image": "682384E6-2714-486C-A716-4757245349A1.jpg",
    },
    "tip-lagrandeboucherie.html": {
        "title": "La Grande Boucherie — The room Midtown doesn't deserve",
        "desc": "Stained glass skylight, zinc bar, seafood on ice.",
        "image": "Screenshot_2026-03-17_at_15_29_23.png",
    },
    "tip-manor.html": {
        "title": "Manor Food Hall — The best grocery in central Geneva",
        "desc": "The fishmonger gets fera from Lake Geneva. Check what's on action.",
        "image": "manor-exterior.jpg",
    },
    "tip-empanadas.html": {
        "title": "Empanadas Factory — Get the Beef Boliviano. Ask for the sauce picante.",
        "desc": "Steak and egg on rice with fries, under CHF 25.",
        "image": "Screenshot_2026-03-17_at_09_24_22.png",
    },
    "tip-merigonde.html": {
        "title": "Mérigonde — Roast beef sandwich, under CHF 10, take it to the park",
        "desc": "Cross the street to Parc Vermont. Eat in the sun.",
        "image": "sandwich-nations.jpg",
    },
    "tip-mulligans.html": {
        "title": "Mulligans Irish Pub — Geneva's best pint of Guinness",
        "desc": "Get salt and vinegar crisps with it. Outside feels like a proper city for an hour.",
        "image": "geneva-mulligans-dog.jpg",
    },
    "tip-enfaim.html": {
        "title": "En Faim — Fresh Mediterranean lunch in central Geneva",
        "desc": "Good hummus, a solid chicken wrap, and the sabich.",
        "image": "enfaim-sabich.jpg",
    },
    "tip-chou.html": {
        "title": "Café Chou — The chou, a good coffee, Parc La Grange nearby",
        "desc": "Named after the little dough ball they make.",
        "image": "eauxvives-chou.jpg",
    },
    "tip-galerie123.html": {
        "title": "Galerie 1 2 3 — Vintage Swiss posters. Expensive, unique, worth it.",
        "desc": "Browse the website first, go in with a specific ask.",
        "image": "galerie123-1.jpg",
    },
    "tip-victoriahall.html": {
        "title": "Victoria Hall — Walk in and the ceiling will stop you",
        "desc": "One of Geneva's most beautiful rooms.",
        "image": "victoria-hall-wide.jpg",
    },
    "tip-swisstrains.html": {
        "title": "Swiss Train Restaurant Car — Nobody seems to know this exists",
        "desc": "White tablecloth, Alps out the window, proper food at 200km/h.",
        "image": "Screenshot_2026-03-17_at_09_39_02.png",
    },
    "tip-papabou.html": {
        "title": "Papabou — Smashburgers and natural wine in Plainpalais",
        "desc": "Swiss potato fries. Having this in Geneva is genuinely comforting.",
        "image": "papabou-burger-wine.jpg",
    },
    "tip-ottolenghi.html": {
        "title": "Ottolenghi Geneva — Out of all the places in the world, Ottolenghi opened here",
        "desc": "The check must have been good. But it's excellent.",
        "image": "ottolenghi-eggs.jpg",
    },
}

# ── MAPS DATA ─────────────────────────────────────────────────────────────────
# Google Maps search URL per tip page
MAPS_URLS = {
    "tip-bongojoe.html":        "https://maps.google.com/?q=Bongo+Joe+Quai+Ernest-Ansermet+3+Geneva",
    "tip-nagomi.html":          "https://maps.google.com/?q=Nagomi+Sushi+Rue+de+Zurich+47+Geneva",
    "tip-labarge.html":         "https://maps.google.com/?q=La+Barge+Promenade+des+Lavandieres+Geneva",
    "tip-baindespaquis.html":   "https://maps.google.com/?q=Bains+des+Paquis+Quai+du+Mont-Blanc+30+Geneva",
    "tip-tanuki.html":          "https://maps.google.com/?q=Tanuki+Sushi+Rue+Vignier+5+Geneva",
    "tip-jlc.html":             "https://maps.google.com/?q=Jaeger+LeCoultre+Rue+du+Rhone+Geneva",
    "tip-paulhenri.html":       "https://maps.google.com/?q=Marche+de+Carouge+Place+du+Marche+Carouge+Geneva",
    "tip-saintamour.html":      "https://maps.google.com/?q=Domaine+Saint-Amour+Lavaux+Vaud+Switzerland",
    "tip-belvedere.html":       "https://maps.google.com/?q=Grand+Hotel+Belvedere+Wengen+Switzerland",
    "tip-arnavutkoy.html":      "https://maps.google.com/?q=Arnavutkoy+Restaurant+Yenikoy+Istanbul",
    "tip-pero.html":            "https://maps.google.com/?q=Pero+Bar+Yenikoy+Istanbul",
    "tip-grea.html":            "https://maps.google.com/?q=Grea+Coffee+Nations+Yenikoy+Istanbul",
    "tip-iskender.html":        "https://maps.google.com/?q=Bursa+Iskenderoglu+Sisli+Istanbul",
    "tip-karmabread.html":      "https://maps.google.com/?q=Karma+Bread+13+South+End+Road+London",
    "tip-electriccinema.html":  "https://maps.google.com/?q=Electric+Cinema+191+Portobello+Road+London",
    "tip-lagrandeboucherie.html":"https://maps.google.com/?q=La+Grande+Boucherie+145+W+53rd+St+New+York",
    "tip-manor.html":           "https://maps.google.com/?q=Manor+Food+Hall+Rue+de+Cornavin+6+Geneva",
    "tip-empanadas.html":       "https://maps.google.com/?q=Empanadas+Factory+Rue+de+Montbrillant+82+Geneva",
    "tip-merigonde.html":       "https://maps.google.com/?q=Merigonde+Boulangerie+Nations+Geneva",
    "tip-mulligans.html":       "https://maps.google.com/?q=Mulligans+Irish+Pub+Rue+De-Grenus+14+Geneva",
    "tip-enfaim.html":          "https://maps.google.com/?q=En+Faim+Rue+Kleberg+12+Geneva",
    "tip-chou.html":            "https://maps.google.com/?q=Cafe+Chou+Rue+des+Eaux-Vives+79+Geneva",
    "tip-galerie123.html":      "https://maps.google.com/?q=Galerie+123+Rue+des+Eaux-Vives+4+Geneva",
    "tip-victoriahall.html":    "https://maps.google.com/?q=Victoria+Hall+Geneva",
    "tip-swisstrains.html":     "https://maps.google.com/?q=Gare+de+Cornavin+Geneva",
    "tip-papabou.html":         "https://maps.google.com/?q=Papabou+Plainpalais+Geneva",
    "tip-ottolenghi.html":      "https://maps.google.com/?q=Ottolenghi+Geneva+Rive",
    "tip-bijougregoire.html":   "https://maps.google.com/?q=Bijouterie+Gregoire+Rue+de+la+Cite+8+Geneva",
}

# ── HTML SNIPPETS ──────────────────────────────────────────────────────────────
OG_BLOCK = '''  <!-- OG / SOCIAL META -->
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="HoodTip" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{base}/{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="800" />
  <meta property="og:url" content="{base}/{filename}" />
  <!-- TWITTER / X -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{base}/{image}" />'''

# Injected right after the closing </div> of .meta-strip
MAPS_BUTTON = '''
  <!-- MAPS + SHARE BUTTONS -->
  <div style="display:flex;gap:0.5rem;margin:1.25rem 0 2rem;">
    <a href="{maps_url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:0.45rem;background:#1a1816;color:#f7f4ef;font-family:'Barlow Condensed',system-ui,sans-serif;font-size:0.64rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;padding:0.65rem 1rem;text-decoration:none;">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
      Open in Maps
    </a>
    <button onclick="(async()=>{{if(navigator.share){{try{{await navigator.share({{title:document.title,url:location.href}})}}catch(e){{}}}}else{{try{{await navigator.clipboard.writeText(location.href);const t=document.getElementById('ht-toast');t.style.opacity='1';setTimeout(()=>t.style.opacity='0',2000)}}catch(e){{}}}}}})()" style="display:inline-flex;align-items:center;gap:0.45rem;background:transparent;color:#6b6560;font-family:'Barlow Condensed',system-ui,sans-serif;font-size:0.64rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;padding:0.65rem 1rem;border:1px solid #e0dbd3;cursor:pointer;">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      Share tip
    </button>
  </div>
  <div id="ht-toast" style="position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:#1a1816;color:#f7f4ef;font-family:'Barlow Condensed',system-ui,sans-serif;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;padding:0.65rem 1.25rem;opacity:0;transition:opacity 0.2s;pointer-events:none;z-index:999;">Link copied</div>'''

# CTA box to inject before </body>  — only on tip pages, only if not already present
POST_CTA = '''
  <!-- LEAVE A TIP CTA -->
  <div style="border:1.5px solid #1a1816;padding:1.75rem 2rem;margin:3rem 0 0;display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:center;">
    <div>
      <div style="font-family:'Cormorant Garamond',Georgia,serif;font-size:1.4rem;font-weight:400;line-height:1.2;margin-bottom:0.35rem;">Know somewhere <em>good?</em></div>
      <p style="font-size:0.78rem;color:#6b6560;line-height:1.65;">A photo, a place, two sentences. We turn it into a proper article with your name on it. Positive only. Specific over general.</p>
    </div>
    <a href="https://hoodtip.com" style="display:inline-block;background:#1a1816;color:#f7f4ef;font-family:'Barlow Condensed',system-ui,sans-serif;font-size:0.63rem;letter-spacing:0.14em;text-transform:uppercase;padding:0.75rem 1.25rem;text-decoration:none;white-space:nowrap;flex-shrink:0;">Leave a HoodTip &rarr;</a>
  </div>'''


# ── HELPERS ────────────────────────────────────────────────────────────────────
def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1) if m else "HoodTip"

def extract_description(html):
    m = re.search(r'<meta name="description" content="(.*?)"', html)
    return m.group(1) if m else "Only the good stuff."

def extract_first_image(html):
    matches = re.findall(r'src="([^"]+\.(jpg|jpeg|png|JPG|webp))"', html)
    for src, _ in matches:
        if not src.startswith('http') and 'fonts' not in src:
            return src
    return "baindespaquis-sunset.jpg"


# ── MAIN ───────────────────────────────────────────────────────────────────────
def process_file(filepath):
    filename = os.path.basename(filepath)
    is_tip = filename.startswith("tip-")

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    changes = []

    # 1. OG TAGS
    if "og:title" not in html:
        if filename in OVERRIDES:
            o = OVERRIDES[filename]
            title, desc, image = o["title"], o["desc"], o["image"]
        else:
            title = extract_title(html)
            desc = extract_description(html)
            image = extract_first_image(html)

        og = OG_BLOCK.format(title=title, desc=desc, image=image,
                             base=BASE_URL, filename=filename)
        html = re.sub(r'(</title>)', r'\1\n' + og, html, count=1)
        changes.append("OG tags")

    # 2. MAPS + SHARE BUTTONS (tip pages only)
    if is_tip and filename in MAPS_URLS and "Open in Maps" not in html:
        maps_url = MAPS_URLS[filename]
        btn = MAPS_BUTTON.format(maps_url=maps_url)
        # Insert after the first closing </div> that follows a meta-strip or meta-row
        # We look for the meta-strip closing tag pattern
        pattern = r'(</div>\s*)(<!-- (?:BODY|body|pull|img|article|TIP BOX)|<div class="body"|<div class="pull-quote"|<p class="subtitle")'
        if re.search(r'class="meta-strip"', html):
            # Find end of meta-strip div
            html = re.sub(
                r'(class="meta-strip"[^<]*(?:<(?!div)[^<]*|<div[^>]*>(?:[^<]|<(?!div))*</div>)*</div>)',
                r'\1' + btn,
                html, count=1, flags=re.DOTALL
            )
        elif re.search(r'class="meta-row"', html):
            html = re.sub(
                r'(class="meta-row"[^<]*(?:<(?!div)[^<]*|<div[^>]*>(?:[^<]|<(?!div))*</div>)*</div>)',
                r'\1' + btn,
                html, count=1, flags=re.DOTALL
            )
        else:
            # Fallback: insert before first <div class="body"> or <p class="subtitle">
            html = re.sub(
                r'(<div class="body">)',
                btn + r'\n  \1',
                html, count=1
            )
        changes.append("Maps button")

    # 3. POST CTA (tip pages only, before </body>)
    if is_tip and "Know somewhere" not in html:
        html = html.replace("</body>", POST_CTA + "\n</body>", 1)
        changes.append("Post CTA")

    if changes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return f"✓  {filename} — {', '.join(changes)}"
    else:
        return f"—  {filename} (nothing to do)"


if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    html_files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".html")
    ])

    if not html_files:
        print("No HTML files found in this folder.")
    else:
        print(f"Found {len(html_files)} HTML files\n")
        updated = skipped = 0
        for path in html_files:
            result = process_file(path)
            print(result)
            if result.startswith("✓"):
                updated += 1
            else:
                skipped += 1

        print(f"\nDone — {updated} updated, {skipped} already complete")
        print("Commit everything to GitHub and you're live.")
