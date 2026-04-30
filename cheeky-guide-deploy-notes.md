# Cheeky Beer Guide — Deploy Notes

## Files to drop into the repo

**The article:**
- `geneva-after-work-beer.html`

**The 10 photos** (all already named for the article — just drop them in repo root):
- `cheeky-guide-nations.jpg` (hero — UN flags at golden hour)
- `cheeky-guide-mr-pickwick-exterior.jpg`
- `cheeky-guide-pickwicks-murphys.jpg` (the Murphy's pint — was IMG_1457)
- `cheeky-guide-publordjim-interior.jpg`
- `cheeky-guide-publordjim-menu.jpg`
- `cheeky-guide-bongojoe-rhoneriver.jpg`
- `cheeky-guide-bongojoe-wine.jpg`
- `cheeky-guide-labarje-beer.jpg`
- `cheeky-guide-labarje-doggy.jpg`
- `cheeky-guide-labarje-wide.jpg`

That's it for the article.

---

## One small sitemap update

Add this entry to your `sitemap.xml` (anywhere inside the `<urlset>` tags):

```xml
  <url>
    <loc>https://hoodtip.com/geneva-after-work-beer.html</loc>
    <lastmod>2026-04-30</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
```

Priority 0.9 because this is meant to be a high-traffic landing page.

---

## One small index.html update (later, when you have time)

When you next touch the homepage, add a teaser block linking to this guide. It's a "Geneva guide" so it lives somewhere distinct from individual tips. Could go below the cover hero, or as a new strip near the contributors block. Don't worry about it for the launch — Google can find it via the sitemap.

---

## What I did to your draft

Light touch. I kept every joke, every aside, every opinion. Specifically:

- **Fixed typos** (beest → best, proximitiy → proximity, disapeaers → disappears, Reign → Reine, publord jims → Pub Lord Jim, etc.)
- **Tightened a few run-ons** without changing what they say
- **Restructured slightly** — gave each place a proper section header so Google indexes them as discrete "best Pub Lord Jim Geneva" type queries
- **Kept all the phrases that make it yours**: "thirsty traveller", "the WEF people on the other side of the lake", "something just off about Pickwicks", the "incredible stuff" Lord Jim aside, "proximity to water always calms the nerves"

---

## Note on the future tip pages

The guide currently links out to `tip-mulligans.html`, `tip-bongojoe.html`, and `tip-labarje.html` — these exist. The other four (Pickwicks, Pub Lord Jim, La Petite Reine, Medusa/Arianna) don't have tip pages yet — they're just paragraphs in the guide.

Whenever you build those tip pages later, this guide will automatically benefit because we can add the same `tip-link` button to each section. Each new tip page = another internal link into this guide = compounding SEO authority.

The Murphy's-at-Pickwicks tip is the obvious next one to build. That's a real opinion only you have.
