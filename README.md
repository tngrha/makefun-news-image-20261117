# The World in One Page — Tuesday 17 November 2026

`main.py` draws a 1024x1024 newspaper-front-page infographic of the world
news of Tuesday 17 November 2026 and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`.

- Masthead names the day: **TUESDAY 17 NOVEMBER 2026**.
- Hero: the collapsed Kerch Bridge — Ukraine's strike brings down part of
  the bridge to Crimea; Russia hits Kyiv's Dnipro bridges, cutting heat,
  water and power.
- Eight story tiles cover Trump in Manila and China, the Hormuz tanker
  mines and the US carrier, Iran's drone attack in Bahrain, the JPMorgan
  outage and Nvidia earnings, the failed Vulcan rocket, the Pentagon's
  9th failed audit, UK sanctions on Israeli firms, and Japan scrambling
  jets on a Russian incursion.
- Footer "Also in brief": Depardieu's guilty plea, congenital measles
  cases, and the Houthi advance in Yemen.

PIL only, DejaVu fonts, no network, no randomness — the output is
byte-identical on every run. Run with:

    MAKEFUN_OUTPUT_DIR=out python3 main.py
