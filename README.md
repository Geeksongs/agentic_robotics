# EmbodiedRSI

Project website for **EmbodiedRSI: Continual Robot Learning Through Hypothesis-Guided Co-Evolution**.

## Anonymous mode

`site-config.json` enables anonymous publication by default. The generated page displays **Anonymous Authors** and omits author names, affiliations, and university logos. The submission PDF is excluded from publication.

Private identity settings and logo backups live in the local, Git-ignored `.site-private/` directory. To restore named authors locally, set `anonymous` to `false` in `site-config.json` and regenerate the website. Named builds require these private settings.

Website anonymity does not remove identity from a hosting account, repository ownership, or existing Git history.

## Preview

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. The site uses local HTML, CSS, and JavaScript. Benchmark tabs support keyboard navigation, and real-robot photo sequences expand independently.

## Regenerate

```sh
python3 -m pip install pymupdf
python3 scripts/build_site.py /path/to/manuscript-directory [real-robot-photos.zip]
```

The source directory contains `iclr2027_conference.tex` and `Figure/`. Regeneration extracts the abstract and results without editing the manuscript. Optional ZIP import preserves the five real-robot task sequences as individual original JPEGs. Existing imported photographs are retained.

Simulation comparisons display RoboCasa365 Composite-Unseen and LIBERO-Pro Overall. Chart values come from the manuscript tables. Source mappings and chart exports remain local in `.site-private/` and are not published. Ablation studies are omitted.

## Deploy

Push to `website`. GitHub Actions publishes `index.html`, `style.css`, `site.js`, and `assets/` to GitHub Pages. Only image assets are copied into the deployment. Private identity settings, JSON data exports, and the manuscript PDF are excluded.
