# EmbodiedRSI

Project website for **EmbodiedRSI: Continual Robot Learning Through Hypothesis-Guided Co-Evolution**.

- Website: https://geeksongs.github.io/agentic_robotics/

The project is branded EmbodiedRSI. The current manuscript and its abstract retain the original method name, EmbodiedEvo. The site uses the manuscript's abstract verbatim (converting LaTeX formatting to HTML), figures, and result tables. The source branch was cloned exclusively from [`realtime-robosuite`'s `website` branch](https://github.com/Geeksongs/realtime-robosuite/tree/website).

## Preview

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. The website is static HTML/CSS/JavaScript with no external runtime dependencies. The visual design uses a split hero, local university logos, a dark benchmark section with keyboard-accessible tabs, and expandable real-robot photo sequences. Logo source URLs are recorded in `assets/logos/sources.json`.

## Regenerate from the manuscript

```sh
python3 -m pip install pymupdf
python3 scripts/build_site.py /path/to/manuscript-directory [real-robot-photos.zip]
```

The source directory should contain `iclr2027_conference.tex`, `Figure/`. The submission PDF is not included in the published website. Regeneration converts existing figures to browser-compatible PNGs and extracts the abstract and tables without editing the manuscript. An optional ZIP imports the five real-robot task photo sequences; the website displays each original JPEG separately, in timestamp order. Existing imported photographs are preserved on subsequent builds. The author list uses two affiliations: Columbia University and Princeton University. Shilong Liu is affiliated with both institutions. Ablation studies are omitted from the website. Simulation comparisons use bar charts for RoboCasa365 Composite-Unseen and LIBERO-Pro Overall, extracted directly from the manuscript tables with downloadable JSON data.

## Deploy

Push to `website`. The GitHub Actions workflow publishes only `index.html`, `style.css`, `site.js`, and `assets/` to GitHub Pages.
