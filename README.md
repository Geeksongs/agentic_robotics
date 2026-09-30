# EmbodiedEvo

Project website for **EmbodiedEvo: Continual Robot Learning through Hypothesis-Guided Co-Evolution**.

- Website: https://geeksongs.github.io/agentic_robotics/
- Paper: [assets/paper/embodied-evo.pdf](assets/paper/embodied-evo.pdf)

The site uses the manuscript's abstract verbatim (converting LaTeX formatting to HTML), figures, and result tables. The source branch was cloned exclusively from [`realtime-robosuite`'s `website` branch](https://github.com/Geeksongs/realtime-robosuite/tree/website).

## Preview

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. The website is static HTML/CSS with no external runtime dependencies.

## Regenerate from the manuscript

```sh
python3 -m pip install pymupdf
python3 scripts/build_site.py /path/to/manuscript-directory
```

The source directory should contain `iclr2027_conference.tex`, its compiled PDF, and `Figure/`. Regeneration converts existing figures to browser-compatible PNGs and extracts the abstract and tables without editing the manuscript.

## Deploy

Push to `website`. The GitHub Actions workflow publishes only `index.html`, `style.css`, and `assets/` to GitHub Pages.
