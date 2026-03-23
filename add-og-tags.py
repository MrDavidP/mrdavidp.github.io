"""
HoodTip — Add OG/Social meta tags to all HTML files
Run this from inside your local repo folder:

    python3 add-og-tags.py

It will add OG tags to every HTML file that doesn't already have them.
Files that already have og:title are left untouched.
"""

import os
import re

BASE_URL = "https://hoodtip.com"

# Per-page overrides — title, description, image
# Any file not listed here gets sensible auto-generated tags
OVERRIDES = {
    "index.html": {
        "title": "HoodTip — Only the good stuff",
        "desc": "Neighbourhood tips from people who actually know. Specific, positive, useful. Geneva, London, Istanbul and beyond.",
        "image": "baindespaquis-sunset.jpg",
    },
    "geneva.html": {
        "title": "Geneva — HoodTip city guide",
        "desc": "The best of Geneva by neighbourhood. Carouge, Plainpalais, Pâquis, Eaux-Vives and beyond. Tips from people who actually live here.",
        "image": "geneva-hero.jpg",
    },
    "istanbul.html": {
        "title": "Istanbul — HoodTip city guide",
        "desc": "Yeniköy, the Bosphorus, raki-balık, roastery cafés. Istanbul tips from people who know it.",
        "image": "istanbul-hero.jpg",
    },
    "london.html": {
        "title": "London — HoodTip city guide",
        "desc": "Notting Hill, Hampstead, the Electric Cinema, best challah in the city. London tips from people who actually live there.",
        "image": "london-hero.jpg",
    },
    "carouge.html": {
        "title": "Carouge — Geneva's best neighbourhood · HoodTip",
        "desc": "Saturday market with a violinist, natural wine, oysters at noon. The neighbourhood that makes Geneva feel like somewhere else entirely.",
        "image": "carouge-cover.jpg",
    },
    "plainpalais.html": {
        "title": "Plainpalais — Geneva · HoodTip",
        "desc": "Bongo Joe on the Rhône, the best takeout sushi in the city, Victoria Hall. Plainpalais tips from people who live here.",
        "image": "plainpalais-hero-3.jpg",
    },
    "saint-gervais.html": {
        "title": "Saint-Gervais — Geneva · HoodTip",
        "desc": "The Manor food hall, Mulligans for a proper pint, En Faim for lunch. The neighbourhood around Cornavin station.",
        "image": "saintgervais-hero-3.jpg",
    },
    "paquis.html": {
        "title": "Pâquis — Geneva · HoodTip",
        "desc": "Nagomi for the best sushi in Geneva. Bains des Pâquis for a cold swim and rosé on the jetty.",
        "image": "paquis-hero-2.jpg",
    },
    "eaux-vives.html": {
        "title": "Eaux-Vives — Geneva · HoodTip",
        "desc": "Café Chou, Galerie 1 2 3 for vintage Swiss posters, and the lake nearby. Tips from the neighbourhood.",
        "image": "eauxvives-streetscene.jpg",
    },
    "nations.html": {
        "title": "Nations — Geneva · HoodTip",
        "desc": "The beating heart of international Geneva. Shockingly few places to eat. Here are the ones worth knowing.",
        "image": "Nations-chair.jpg",
    },
    "cornavin.html": {
        "title": "Cornavin — Geneva · HoodTip",
        "desc": "Geneva's main station. The Swiss intercity restaurant car: white tablecloth, Alps out the window at 200km/h. Nobody seems to know it exists.",
        "image": "cornavin-station-1.jpg",
    },
    "notting-hill.html": {
        "title": "Notting Hill — London · HoodTip",
        "desc": "The Electric Cinema, The Cow, pastel houses on Portobello Road. Notting Hill tips from people who actually know it.",
        "image": "IMG_6278.JPG",
    },
    "yenikoy.html": {
        "title": "Yeniköy — Istanbul · HoodTip",
        "desc": "Raki-balık on the Bosphorus, a roastery café with cats, a bar you won't want to leave. Yeniköy tips from people who know it.",
        "image": "photo-arnavutkoy-restaurant.jpg",
    },
    "profile-dave.html": {
        "title": "Dave — 49 tips across 7 cities · HoodTip",
        "desc": "Natural wine, proper pubs, waterfront bars, good fish, Saturday markets. Geneva-based. The person who built HoodTip.",
        "image": "bongojoe-rhone-light.jpg",
    },
    "profile-paddy.html": {
        "title": "Patrick Eisenstein — HoodTip contributor",
        "desc": "Spends more time looking at watch movements than is strictly healthy. 1 tip in Geneva: the best NOMOS destination in the city.",
        "image": "nomos-6.jpg",
    },
    "profile-build.html": {
        "title": "Build your HoodTip profile — share the good stuff",
        "desc": "Not a follower count. Not a star rating. Just the places you actually know, filed by neighbourhood, written for the next person who ends up there.",
        "image": "baindespaquis-sunset.jpg",
    },
    "tip-bongojoe.html": {
        "title": "Bongo Joe — A record shop that became Geneva's best outdoor bar",
        "desc": "Sit on the Rhône, order the local white, ask for the nuts. One of the only places in Geneva that feels genuinely relaxed.",
        "image": "bongojoe-yellow-table.jpg",
    },
    "tip-nagomi.html": {
        "title": "Nagomi — The best sushi in Geneva. You are briefly in Tokyo.",
        "desc": "Sit at the bar, order the uni, drink cold sake. The chef has been doing this a long time.",
        "image": "nagomi-chef.jpg",
    },
    "tip-labarge.html": {
        "title": "La Barge — Jump in the Rhône, drink a cold beer, repeat",
        "desc": "A little summer bar right on the water. The best spot in Geneva for submerging your body in cold, fast, clean water.",
        "image": "barge-water-example.jpg",
    },
    "tip-baindespaquis.html": {
        "title": "Bains des Pâquis — 70s vibes on Lac Léman",
        "desc": "Cold rosé on the jetty, jump off the board, Alps right there. Geneva institution since 1932. Everyone knows about it, not enough people go.",
        "image": "baindespaquis-sunset.jpg",
    },
    "tip-tanuki.html": {
        "title": "Tanuki — Really good sushi. Homemade wasabi. Takeout only.",
        "desc": "An elderly Japanese couple running a takeout sushi operation in Plainpalais. Get the large platter. Stop at Uchitomi for sake on the way home.",
        "image": "tanuki-on-table.jpg",
    },
    "tip-jlc.html": {
        "title": "Jaeger-LeCoultre — The luxury watch you can actually buy in Geneva",
        "desc": "You can't walk out of a Rolex boutique with a watch. JLC on Rue du Rhône you can. Walk in, buy a watch, leave with it.",
        "image": "jlc_river.jpg",
    },
    "tip-paulhenri.html": {
        "title": "Paul-Henri Soler — The best wine at the Carouge Saturday market",
        "desc": "CHF 17. Free tastings. Get there before noon. The Saturday market wine everyone who lives here already knows about.",
        "image": "carouge-wine-bottles.jpg",
    },
    "tip-saintamour.html": {
        "title": "Domaine Saint-Amour — Honour system rosé in a UNESCO vineyard",
        "desc": "Leave money in the box, take a bottle of rosé, sit in the vines above Lake Geneva. One of those afternoons.",
        "image": "saintamour-lavaux-lake.jpg",
    },
    "tip-belvedere.html": {
        "title": "Grand Hotel Belvedere — Stay here for most of your meals in Wengen",
        "desc": "The sommelier is doing incredible wines from Germany and Switzerland. The chef is making some of the best food in the country. Don't eat out.",
        "image": "wengen-belvedere-pool-snow.jpg",
    },
    "tip-arnavutkoy.html": {
        "title": "Arnavutköy Restaurant — Raki-balık on the Bosphorus",
        "desc": "Sit outside, order the salad first, drink raki slowly. One of those meals that makes you understand why people love Istanbul.",
        "image": "photo-arnavutkoy-restaurant.jpg",
    },
    "tip-pero.html": {
        "title": "Pero — Arrive for one drink. Leave hours later.",
        "desc": "A bar in Yeniköy on the Bosphorus. The kind of place that has no right to be this good. Go.",
        "image": "IMG_7505.JPG",
    },
    "tip-grea.html": {
        "title": "Grea Coffee Nations — Roastery café in Yeniköy with a courtyard and cats",
        "desc": "They roast on site and supply half of Istanbul's better cafés. The kind of spot you find on a morning walk and stay longer than planned.",
        "image": "photo-roastery-cafe.jpg",
    },
    "tip-iskender.html": {
        "title": "Bursa İskenderoğlu — The İskender kebab. Go here. Get this.",
        "desc": "Lamb over bread, under butter and tomato sauce, yogurt on the side. The family connection to the 1860s Bursa original is real.",
        "image": "Iskender-Bursa.jpg",
    },
    "tip-karmabread.html": {
        "title": "Karma Bread — Best challah in London. Come on Friday.",
        "desc": "That's when they bake it and it goes fast. Pick one up, walk Hampstead Heath, go home.",
        "image": "london-karmabread-challah-hand.jpg",
    },
    "tip-electriccinema.html": {
        "title": "Electric Cinema — Britain's oldest cinema, still the best one to sit in",
        "desc": "Leather sofa seats, a lamp on your armrest, a glass of champagne. Notting Hill's Electric Cinema is in a different category.",
        "image": "682384E6-2714-486C-A716-4757245349A1.jpg",
    },
    "tip-lagrandeboucherie.html": {
        "title": "La Grande Boucherie — The room Midtown doesn't deserve",
        "desc": "Stained glass skylight, zinc bar, seafood on ice. The 45 minutes where Midtown stops being Midtown.",
        "image": "Screenshot_2026-03-17_at_15_29_23.png",
    },
    "tip-manor.html": {
        "title": "Manor Food Hall — The best grocery in central Geneva",
        "desc": "The fishmonger gets fera from Lake Geneva. Check what's on action at the meat counter before deciding what to cook.",
        "image": "manor-exterior.jpg",
    },
    "tip-empanadas.html": {
        "title": "Empanadas Factory — Get the Beef Boliviano. Ask for the sauce picante.",
        "desc": "Steak and egg on rice with fries, under CHF 25. One of the few genuinely good options near the UN in Geneva.",
        "image": "Screenshot_2026-03-17_at_09_24_22.png",
    },
    "tip-merigonde.html": {
        "title": "Mérigonde — Roast beef sandwich, under CHF 10, take it to the park",
        "desc": "Cross the street to Parc Vermont. Eat in the sun. One of the better lunches near the UN.",
        "image": "sandwich-nations.jpg",
    },
    "tip-mulligans.html": {
        "title": "Mulligans Irish Pub — Geneva's best pint of Guinness",
        "desc": "Get salt and vinegar crisps with it. Outside feels like a proper city for an hour. Which in Geneva is rarer than you'd think.",
        "image": "geneva-mulligans-dog.jpg",
    },
    "tip-enfaim.html": {
        "title": "En Faim — Fresh Mediterranean lunch in central Geneva",
        "desc": "Good hummus, a solid chicken wrap, and the sabich — fried aubergine, egg, tahini in a pita.",
        "image": "enfaim-sabich.jpg",
    },
    "tip-chou.html": {
        "title": "Café Chou — The chou, a good coffee, Parc La Grange nearby",
        "desc": "Named after the little dough ball they make. Light, slightly crisp outside, properly soft inside. Eaux-Vives, Geneva.",
        "image": "eauxvives-chou.jpg",
    },
    "tip-galerie123.html": {
        "title": "Galerie 1 2 3 — Vintage Swiss posters. Expensive, unique, worth it.",
        "desc": "Old Jungfrau Bahn posters from the 1940s. Browse the website first, go in with a specific ask.",
        "image": "galerie123-1.jpg",
    },
    "tip-victoriahall.html": {
        "title": "Victoria Hall — Walk in and the ceiling will stop you",
        "desc": "One of Geneva's most beautiful rooms. Go for a concert on a Tuesday and feel like you live in a different century.",
        "image": "victoria-hall-wide.jpg",
    },
    "tip-swisstrains.html": {
        "title": "Swiss Train Restaurant Car — Nobody seems to know this exists",
        "desc": "Don't book first class. Buy a standard ticket and walk to the restaurant car. White tablecloth, Alps out the window, proper food at 200km/h.",
        "image": "Screenshot_2026-03-17_at_09_39_02.png",
    },
    "tip-papabou.html": {
        "title": "Papabou — Smashburgers and natural wine in Plainpalais",
        "desc": "Swiss potato fries. Having this in Geneva is genuinely comforting.",
        "image": "papabou-burger-wine.jpg",
    },
    "tip-ottolenghi.html": {
        "title": "Ottolenghi Geneva — Out of all the places in the world, Ottolenghi opened here",
        "desc": "The check must have been good. But it's excellent. Rive, Geneva.",
        "image": "ottolenghi-eggs.jpg",
    },
}

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


def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1) if m else "HoodTip"


def extract_description(html):
    m = re.search(r'<meta name="description" content="(.*?)"', html)
    return m.group(1) if m else "Only the good stuff."


def extract_first_image(html):
    # Find first img src that looks like a local image
    matches = re.findall(r'src="([^"]+\.(jpg|jpeg|png|JPG|webp))"', html)
    for src, _ in matches:
        if not src.startswith('http') and 'fonts' not in src:
            return src
    return "baindespaquis-sunset.jpg"


def process_file(filepath):
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    if "og:title" in html:
        return f"SKIP  {filename} (already has OG tags)"

    # Get data — override or auto-detect
    if filename in OVERRIDES:
        o = OVERRIDES[filename]
        title = o["title"]
        desc = o["desc"]
        image = o["image"]
    else:
        title = extract_title(html)
        desc = extract_description(html)
        image = extract_first_image(html)

    og = OG_BLOCK.format(
        title=title,
        desc=desc,
        image=image,
        base=BASE_URL,
        filename=filename
    )

    updated = re.sub(r'(</title>)', r'\1\n' + og, html, count=1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated)

    return f"✓     {filename}"


if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    html_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".html")
    ]

    if not html_files:
        print("No HTML files found in this folder.")
    else:
        print(f"Found {len(html_files)} HTML files\n")
        skipped = updated = 0
        for path in sorted(html_files):
            result = process_file(path)
            print(result)
            if result.startswith("✓"):
                updated += 1
            else:
                skipped += 1

        print(f"\nDone — {updated} updated, {skipped} already had OG tags")
        print("Commit everything to GitHub and you're live.")
