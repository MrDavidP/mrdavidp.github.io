#!/usr/bin/env python3
"""
HoodTip v2 patcher.

Reads every tip-*.html file in a source directory, extracts the key content
(title, subtitle, pull quote, address, neighbourhood, best-for, category,
all photos with captions), and re-renders each one into the new one-screen
postcard template.

Usage:
    python3 patch_tips.py --src ./old-tips --out ./new-tips

Requires only Python 3 standard library.
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote


# --------- EXTRACTION ---------

def strip_tags(t):
    if not t: return ''
    t = re.sub(r'<br\s*/?>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def first(pattern, source, flags=re.DOTALL):
    m = re.search(pattern, source, flags)
    return m.group(1).strip() if m else ''


def extract(tip_html: str, filename: str) -> dict:
    """Pull every field we care about from a tip HTML file."""
    s = tip_html

    # --- Title ---
    title_raw = first(r'<h1[^>]*>(.*?)</h1>', s)
    title = strip_tags(title_raw) or 'HoodTip'
    # Replace merged-title artifacts (no space after period) with a space
    title = re.sub(r'([a-z.!?])([A-Z])', r'\1 \2', title)
    title = re.sub(r'\s+', ' ', title).strip()
    # Only truncate titles longer than 80 chars
    if len(title) > 80:
        m = re.match(r'([^.!?]+[.!?])', title)
        if m: title = m.group(1).strip()

    # --- Subtitle ---
    subtitle = strip_tags(first(r'class="subtitle"[^>]*>(.*?)</p>', s))
    if not subtitle:
        subtitle = strip_tags(first(r'class="tip-header-subtitle"[^>]*>(.*?)</div>', s))

    # --- Pull quote (the gold) ---
    pq = strip_tags(first(r'class="pull-quote"[^>]*>\s*<p[^>]*>(.*?)</p>', s))
    if not pq:
        pq = strip_tags(first(r'class="tip-pullquote"[^>]*>(.*?)</', s))
    # Strip outer quotes if present
    pq = re.sub(r'^[""\'"]+|[""\'"]+$', '', pq).strip()

    # Fall back to subtitle if no pull quote
    if not pq and subtitle:
        pq = subtitle
    # Final fallback: og description
    if not pq:
        pq = strip_tags(first(r'property="og:description" content="([^"]+)"', s))
    # If pull quote is basically the same as title, discard it
    def normalize(t): return re.sub(r'[^a-z0-9]', '', t.lower())
    if pq and normalize(pq) == normalize(title):
        pq = ''
    if not pq:
        # Try meta description
        pq = strip_tags(first(r'name="description" content="([^"]+)"', s))
        if pq and normalize(pq) == normalize(title):
            pq = ''
    if not pq:
        pq = 'Go. Order the thing. You\'ll see.'

    # --- Category ---
    cat = strip_tags(first(r'class="category"[^>]*>(.*?)</span>', s))
    # Normalize separators
    cat = cat.replace('·', ' · ')
    cat = re.sub(r'\s+', ' ', cat).strip()

    # --- Address / Neighbourhood / Best for ---
    addr = strip_tags(first(r'Address</span>\s*<span class="meta-value">([^<]+)', s))
    hood = strip_tags(first(r'Neighbourhood</span>\s*<span class="meta-value">([^<]+)', s))
    bestfor = strip_tags(first(r'Best for</span>\s*<span class="meta-value">([^<]+)', s))

    # --- All body images (deduplicated, ordered) ---
    body_start = s.find('<body')
    body = s[body_start:] if body_start >= 0 else s
    img_matches = re.findall(
        r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|webp|JPG|JPEG|PNG|WEBP))"'
        r'(?:[^>]*alt="([^"]*)")?',
        body
    )
    seen = set()
    images = []
    for src, alt in img_matches:
        key = src.lower()
        if key in seen: continue
        # Skip avatars, logo, ui chrome
        low = src.lower()
        if 'bongojoe' in low or 'avatar' in low or 'logo' in low: continue
        if src.startswith('data:') or src.startswith('http'): continue
        seen.add(key)
        images.append({'src': src, 'alt': alt or title})

    # First image is hero
    hero_image = images[0]['src'] if images else ''

    # --- Meta description ---
    meta_desc = strip_tags(first(r'name="description" content="([^"]+)"', s))
    og_desc = strip_tags(first(r'property="og:description" content="([^"]+)"', s))

    # --- City (derive from neighbourhood or address or category) ---
    city = ''
    if hood and ',' in hood:
        parts = [p.strip() for p in hood.split(',')]
        if len(parts) >= 2:
            city = parts[-1]
    if not city and addr:
        m = re.search(r',\s*(?:\d{4,5}\s+)?([A-Z][A-Za-zéèêàâôöüñ\-]+)(?:\s+[A-Z]{2})?\s*$', addr)
        if m: city = m.group(1)
    if not city and cat:
        parts = [p.strip() for p in cat.split('·')]
        if len(parts) >= 2:
            city = parts[-1]
    # Last resort: scan title/pull quote/og_desc for known cities
    if not city:
        known_cities = [
            'Geneva','Genève','Zurich','Zürich','Bern','Wengen','Lausanne','Lavaux',
            'Paris','London','New York','Tokyo','Istanbul','Athens','Barcelona',
            'Lusaka','Kigali','Nouakchott','Arusha','Zanzibar','Nungwi','Tel Aviv',
            'Cape Town','Subotica','Mykonos','Astypalea','Plainpalais','Eaux-Vives',
            'Carouge','Pâquis','Exarchia','Sarona','Notting Hill','Midtown','Soho',
            'Chêne','Rive','Mauritania','Rwanda','Switzerland','Greece','Turkey',
            'France','Italy','Spain',
        ]
        og_desc_val = strip_tags(first(r'property="og:description" content="([^"]+)"', s))
        meta_desc_val = strip_tags(first(r'name="description" content="([^"]+)"', s))
        haystack = ' '.join([title, subtitle, pq, og_desc_val, meta_desc_val])
        for c in known_cities:
            if re.search(r'\b' + re.escape(c) + r'\b', haystack):
                city = c
                break

    return {
        'filename': filename,
        'slug': filename.replace('.html', ''),
        'title': title,
        'subtitle': subtitle,
        'pull_quote': pq,
        'category': cat,
        'address': addr,
        'neighbourhood': hood,
        'city': city,
        'best_for': bestfor,
        'hero_image': hero_image,
        'images': images,
        'meta_desc': meta_desc or og_desc or pq,
        'og_desc': og_desc or pq,
    }


# --------- TRANSFORMATION ---------

def derive_badge(category: str, title: str) -> str:
    """Pick the first category word for the top-right badge."""
    if not category: return 'Tip'
    parts = [p.strip() for p in re.split(r'[·/,]', category) if p.strip()]
    if parts:
        word = parts[0]
        # Capitalize first letter
        return word[:1].upper() + word[1:]
    return 'Tip'


def derive_breadcrumb(hood: str, city: str, category: str, title: str) -> tuple:
    """Return (middle, last) breadcrumb parts.

    Examples:
      "HoodTip / Geneva / Plainpalais"  (city + hood)
      "HoodTip / Geneva"                (city only)
      "HoodTip / Hotel"                 (no city, use category)
      "HoodTip"                         (nothing)
    """
    if city and hood:
        hood_clean = hood.split(',')[0].strip()
        if hood_clean.lower() == city.lower():
            return '', html.escape(city)
        return f'<span>/</span><a href="index.html">{html.escape(city)}</a>', html.escape(hood_clean)
    if city:
        return '', html.escape(city)
    if hood:
        return '', html.escape(hood.split(',')[0].strip())
    # Fall back to category word (but never the title)
    if category:
        parts = [p.strip() for p in re.split(r'[·/]', category) if p.strip()]
        if parts: return '', html.escape(parts[0])
    return '', ''


def derive_location_line(category: str, hood: str, city: str) -> str:
    """The thin kicker line above the title."""
    bits = []
    cat_first = ''
    if category:
        parts = [p.strip() for p in re.split(r'[·/]', category) if p.strip()]
        if parts: cat_first = parts[0]
    if cat_first: bits.append(cat_first)
    if hood:
        hood_clean = hood.split(',')[0].strip()
        if hood_clean and hood_clean != cat_first: bits.append(hood_clean)
    if city and city not in bits: bits.append(city)
    # Join with " · "
    sep = '<span>·</span>'
    return f'<span>/</span>' + sep.join(html.escape(b) for b in bits) if bits else '<span>/</span>HoodTip'


def derive_fact_where(address: str, title: str, city: str) -> str:
    """The 'Where' fact: short address + Google Maps link."""
    if address:
        short = address
        short = re.sub(r',\s*\d{4,5}.*$', '', short).strip()
        if len(short) > 32:
            short = short[:30].rsplit(' ', 1)[0] + '…'
        query = quote(f'{title} {city or ""} {address}')
        return f'<a href="https://maps.google.com/?q={query}" target="_blank" rel="noopener">{html.escape(short)}</a>'
    # No address: link by name + city
    query = quote(f'{title} {city or ""}')
    if city:
        label = html.escape(city)
    else:
        label = 'Find on Maps'
    return f'<a href="https://maps.google.com/?q={query}" target="_blank" rel="noopener">{label}</a>'


def derive_fact_bestfor(best_for: str, category: str) -> str:
    """The 'Best for' fact."""
    if best_for:
        parts = [p.strip() for p in best_for.split(',')]
        if len(parts) >= 2:
            return f'{html.escape(parts[0].capitalize())}, <em>{html.escape(parts[1])}</em>'
        return html.escape(best_for.capitalize())
    if category:
        parts = [p.strip() for p in re.split(r'[·/]', category) if p.strip()]
        if parts:
            # Primary category → implied use case
            cat_map = {
                'hotel': 'Sleep, <em>the next trip</em>',
                'restaurant': 'A good meal',
                'bar': 'A drink, <em>the right one</em>',
                'café': 'Coffee, <em>a pause</em>',
                'cafe': 'Coffee, <em>a pause</em>',
                'wine': 'A bottle, <em>a glass</em>',
                'sushi': 'Dinner, <em>sit at the bar</em>',
                'pizza': 'Dinner, <em>takeaway</em>',
                'market': 'Saturday morning',
                'shop': 'The one item worth it',
                'cinema': 'A good night',
                'deli': 'The sandwich',
                'bakery': 'Breakfast, <em>a loaf</em>',
                'boulangerie': 'Breakfast, <em>a loaf</em>',
                'art': 'An afternoon',
                'library': 'Laptop work',
                'travel': 'The long way',
                'bistro': 'Dinner in Paris',
                'swimming': 'A swim, <em>a drink after</em>',
                'hotel · spa · restaurant': 'The whole trip',
            }
            key = parts[0].lower()
            if key in cat_map:
                return cat_map[key]
            return html.escape(parts[0].capitalize())
    return '<em>A good time</em>'


def derive_fact_move(pull_quote: str, title: str, best_for: str = '') -> str:
    """The 'The move' fact — extract a short imperative."""
    # If best_for has a secondary entry, use it (e.g. "takeaway")
    if best_for:
        parts = [p.strip() for p in best_for.split(',')]
        if len(parts) >= 2:
            return f'<em>{html.escape(parts[1])}</em>'
    if not pull_quote:
        return '<em>Just go</em>'
    # Strip quotes
    pq = pull_quote.strip('"""\'')
    # Look for short imperative sentences
    sents = re.split(r'(?<=[.!?])\s+', pq)
    # Prefer sentences starting with a verb / order
    imperatives = []
    for s in sents:
        s = s.strip()
        if not s: continue
        # Check if it's a short imperative (<40 chars, starts with capital verb)
        if 8 < len(s) < 42 and re.match(r'^(?:Sit|Go|Order|Get|Ask|Try|Stand|Skip|Book|Walk|Drink|Eat|Take|Stop|Accept|Come|Watch|Share|Find|Leave)', s):
            imperatives.append(s)
    if imperatives:
        move = imperatives[0]
    else:
        # Fall back to shortest sentence between 10 and 50 chars
        short = [s.strip() for s in sents if 10 < len(s.strip()) < 50]
        move = short[0] if short else (sents[0] if sents else pq)
    move = move.strip().rstrip('.!?')
    if len(move) > 42:
        move = move[:40].rsplit(' ', 1)[0] + '…'
    return f'<em>{html.escape(move)}</em>'


def format_title(title: str) -> str:
    """Clean title, italicize the final clause if multi-sentence."""
    title = title.strip()
    # Match "First sentence. Final clause." pattern; italicize the final clause.
    # e.g. "Go to Wengen. Stay at the Belvedere. Stop searching."
    #      => "Go to Wengen. Stay at the Belvedere. <em>Stop searching.</em>"
    m = re.match(r'^(.+?[.!?])\s+(.+[.!?])$', title)
    if m:
        head = m.group(1).strip()
        tail = m.group(2).strip()
        # Only italicize the tail if it's not absurdly long
        if len(tail) < 40:
            return f'{html.escape(head)} <em>{html.escape(tail)}</em>'
    return html.escape(title)


def format_callout(pq: str) -> str:
    """Format pull quote with red emphasis on key phrases."""
    pq = pq.strip().strip('"""\'')
    # Preserve em tags from original? No, too messy. Keep plain.
    # Add soft emphasis: bold the shortest standalone clause if exists
    # For safety just escape, no auto-bolding (risky on varied text)
    return html.escape(pq)


def build_slides(images: list, title: str) -> str:
    """Build the <div class='pc-slide'> elements."""
    if not images:
        return (
            '<div class="pc-slide">'
            f'<div class="pc-slide-fallback">§</div>'
            '</div>'
        )
    parts = []
    for i, img in enumerate(images):
        src = html.escape(img['src'], quote=True)
        alt = html.escape(img.get('alt', title) or title, quote=True)
        parts.append(
            f'<div class="pc-slide">'
            f'<img src="{src}" alt="{alt}" loading="{"eager" if i == 0 else "lazy"}" />'
            f'<div class="pc-slide-fallback" style="display:none;">§</div>'
            f'</div>'
        )
    return '\n      '.join(parts)


def build_dots(n: int) -> str:
    if n <= 1: return ''
    return ''.join(
        f'<button class="pc-dot{" active" if i == 0 else ""}" aria-label="Photo {i+1}"></button>'
        for i in range(n)
    )


def render(data: dict, template: str) -> str:
    title_plain = data['title']
    city = data.get('city', '')

    # Page title for <title>
    page_title_bits = [title_plain]
    if city: page_title_bits.append(city)
    page_title_bits.append('HoodTip')
    page_title = ' — '.join(page_title_bits)

    # Share text (WhatsApp)
    share_text = quote(f"{title_plain} — https://hoodtip.com/{data['slug']}.html")

    slides = build_slides(data['images'], title_plain)
    total = max(1, len(data['images']))
    dots = build_dots(total)
    single_class = ' single' if total <= 1 else ''
    many_class = ' many-photos' if total > 8 else ''

    middle, last = derive_breadcrumb(
        data.get('neighbourhood', ''), city, data.get('category', ''), title_plain
    )
    breadcrumb_last_wrapped = f'<span>/</span>{last}' if last else ''

    # Title class for long titles
    title_char_count = len(title_plain)
    if title_char_count > 70:
        title_class = ' xlong'
    elif title_char_count > 40:
        title_class = ' long'
    else:
        title_class = ''

    replacements = {
        '{{PAGE_TITLE}}': html.escape(page_title),
        '{{META_DESC}}': html.escape(data['meta_desc'])[:180],
        '{{OG_TITLE}}': html.escape(f"{title_plain} · HoodTip"),
        '{{OG_DESC}}': html.escape(data['og_desc'])[:180],
        '{{HERO_IMAGE}}': html.escape(data['hero_image']) if data['hero_image'] else 'og-fallback.jpg',
        '{{SLUG}}': html.escape(data['slug']),
        '{{SLIDES}}': slides,
        '{{DOTS}}': dots,
        '{{TOTAL}}': str(total),
        '{{SINGLE_CLASS}}': single_class + many_class,
        '{{BREADCRUMB_MIDDLE}}': middle,
        '{{BREADCRUMB_LAST_WRAPPED}}': breadcrumb_last_wrapped,
        '{{BADGE}}': html.escape(derive_badge(data.get('category', ''), title_plain)),
        '{{CAPTION}}': html.escape(data.get('subtitle', '') or f"{title_plain}."),
        '{{LOCATION_LINE}}': derive_location_line(
            data.get('category', ''), data.get('neighbourhood', ''), city
        ),
        '{{TITLE}}': format_title(title_plain),
        '{{TITLE_CLASS}}': title_class,
        '{{PULL_QUOTE}}': format_callout(data['pull_quote']),
        '{{FACT_WHERE}}': derive_fact_where(data.get('address', ''), title_plain, city),
        '{{FACT_BESTFOR}}': derive_fact_bestfor(data.get('best_for', ''), data.get('category', '')),
        '{{FACT_MOVE}}': derive_fact_move(data['pull_quote'], title_plain, data.get('best_for', '')),
        '{{SHARE_TEXT}}': share_text,
    }

    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


# --------- MAIN ---------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='Directory with old tip-*.html files')
    ap.add_argument('--template', required=True, help='Path to tip-template.html')
    ap.add_argument('--out', required=True, help='Output directory for new tips')
    ap.add_argument('--only', default='', help='Comma-separated list of tip slugs to process (for testing)')
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.template) as f:
        template = f.read()

    only = set(args.only.split(',')) if args.only else None

    files = sorted([f for f in os.listdir(src) if f.startswith('tip-') and f.endswith('.html')])
    print(f'Found {len(files)} tip files')

    ok = 0
    errors = []
    warnings = []

    for fname in files:
        slug = fname.replace('.html', '')
        if only and slug not in only: continue

        try:
            src_path = src / fname
            with open(src_path) as f:
                content = f.read()

            data = extract(content, fname)

            # Warnings for tips with sparse content
            w = []
            if not data['pull_quote'] or data['pull_quote'] == 'Go. Order the thing. You\'ll see.':
                w.append('no pull quote')
            if not data['images']:
                w.append('no images')
            if not data['address'] and not data['neighbourhood']:
                w.append('no location')
            if w:
                warnings.append(f'{fname}: ' + ', '.join(w))

            output = render(data, template)

            with open(out / fname, 'w') as f:
                f.write(output)
            ok += 1
        except Exception as e:
            errors.append(f'{fname}: {type(e).__name__}: {e}')

    print(f'\n✅ Processed: {ok}/{len(files)}')
    if warnings:
        print(f'\n⚠️  {len(warnings)} tips with sparse content:')
        for w in warnings[:20]:
            print(f'    {w}')
        if len(warnings) > 20:
            print(f'    ... and {len(warnings) - 20} more')
    if errors:
        print(f'\n❌ {len(errors)} errors:')
        for e in errors:
            print(f'    {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
