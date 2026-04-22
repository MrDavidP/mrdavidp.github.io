HoodTip v2 — One-screen postcard tips with photo carousels
===========================================================

WHAT'S IN THIS ZIP
------------------
• 61 tip-*.html files — your entire tip library, re-rendered in the new template
• _tip-template.html — the master template (underscore prefix so it sorts first)
• _patch_tips.py — the Python script that generates tips from source
• README.txt — this file

HOW TO DEPLOY
-------------
1. Unzip locally
2. Drag-and-drop all 61 tip-*.html files into your GitHub repo root via the web UI
   (they will overwrite the old tip pages with the same filenames)
3. Commit. GitHub Pages rebuilds automatically. Done.

Nothing else needs to change. All image filenames are preserved exactly as your
existing tips reference them. The same photos on your tip pages today will appear
as carousel slides on the new pages.

WHAT THE NEW TIPS LOOK LIKE
---------------------------
• One screen — no scroll on desktop
• LEFT: photo carousel (swipe, arrows, dots, keyboard arrows)
• RIGHT: category line / title / pull quote callout / 3 facts / byline + share
• Copy Link button and WhatsApp share pre-filled with the tip URL

NOTES ABOUT THE PATCHER
-----------------------
You don't need to run _patch_tips.py — the 61 HTML files are already generated.
It's included so if you want to regenerate in the future (after adding new tips
to the old format, or after editing the template), you can run:

    python3 _patch_tips.py \
        --src ./old-tips \
        --template ./_tip-template.html \
        --out ./new-tips

TIPS WITH SPARSE SOURCE DATA
----------------------------
A handful of your older tips were missing fields (no address, no meta).
The patcher handles this gracefully with smart defaults:
- Missing address → "Find on Maps" linking to a search for the place
- Missing best-for → category-aware default ("Sleep, the next trip" for hotels, etc.)
- Missing pull quote → falls back to subtitle, then to meta description

KNOWN MINOR ISSUES
------------------
• A few tips don't have the perfect city detected (e.g. Saint-Amour shows Geneva
  instead of Lavaux because Geneva appears first in the text). Easy to fix later.
• The footer nav link from the old template ("Plainpalais", "← Back to city")
  is gone — the breadcrumb at the top now serves that role.

NEXT STEPS (after deploying tips)
---------------------------------
- Update index.html to match this aesthetic and new framing
- Update profile-dave.html + profile-build.html
