"""Build the static project page from the provided paper and figures.
Usage: python3 scripts/build_site.py /path/to/paper-directory [real-robot-photos.zip]
Requires: PyMuPDF (pip install pymupdf).
"""
from pathlib import Path
import html
import re
import shutil
import sys
import json
from zipfile import ZipFile
import pymupdf as fitz

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).resolve()
tex = (source / 'iclr2027_conference.tex').read_text()

config = json.loads((root / 'site-config.json').read_text())
anonymous = config.get('anonymous', True)
private = root / '.site-private'
private.mkdir(exist_ok=True)
if anonymous:
    hero_identity = '<p class="anonymous-authors">Anonymous Authors</p>'
    shutil.rmtree(root / 'assets/logos', ignore_errors=True)
else:
    identity = json.loads((private / 'identity.json').read_text())
    authors = ', '.join(f'<span>{html.escape(author["name"])}<sup>{",".join(map(str, author["affiliations"]))}</sup></span>' for author in identity['authors'])
    units = ''.join(f'<span><sup>{unit["number"]}</sup> {html.escape(unit["name"])}</span>' for unit in identity['affiliations'])
    logos = ''.join(f'<a href="{html.escape(unit["url"])}" aria-label="{html.escape(unit["name"])}"><img src="assets/logos/{html.escape(unit["logo"])}" alt="{html.escape(unit["name"])}" width="230" height="64"></a>' for unit in identity['affiliations'])
    (root / 'assets/logos').mkdir(parents=True, exist_ok=True)
    for unit in identity['affiliations']:
        shutil.copy2(private / 'logos' / unit['logo'], root / 'assets/logos' / unit['logo'])
    hero_identity = f'<div class="authors" aria-label="Authors">{authors}</div><div class="affiliations">{units}</div><div class="university-logos">{logos}</div>'

figures = root / 'assets/figures'
figures.mkdir(parents=True, exist_ok=True)

def plain(value):
    value = re.sub(r'\\(?:textbf|text|emph|mathrm)\{([^{}]*)\}', r'\1', value)
    value = value.replace(r'\%', '%').replace(r'\times', '×').replace(r'\uparrow', '↑')
    value = value.replace(r'\pi_{0.5}', 'π₀.₅').replace(r'\pi_0', 'π₀').replace(r'\pi_{RLinf}', 'π_RLinf')
    return html.escape(value.replace('$', '').strip())

abstract_tex = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
abstract_tex = re.sub(r'(?m)^%.*\n?', '', abstract_tex)
abstract = re.sub(r'\s+', ' ', abstract_tex).strip()
abstract = plain(abstract)
for name, dest in [('Main_figure.pdf','overview'), ('Figure 3.pdf','hypothesis-graph'), ('sticker_robot_learning.pdf','evolution-loop')]:
    with fitz.open(source / 'Figure' / name) as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(2,2), alpha=False).save(figures / f'{dest}.png')
for image in (source / 'Figure').glob('*.png'):
    shutil.copy2(image, figures / image.name)

# Preserve each original photograph as its own browser image.
photo_dir = figures / 'real_robot'
photo_dir.mkdir(exist_ok=True)
for photo in (source / 'Figure' / 'real_robot').glob('*.jpg'):
    if not (photo_dir / photo.name).exists():
        shutil.copy2(photo, photo_dir / photo.name)
if len(sys.argv) > 2:
    folders = {'奥利奥': 'oreo', '德州': 'chip', '午餐肉': 'cake', 'glasses': 'glasses', '毛巾': 'towel'}
    provenance = {}
    with ZipFile(sys.argv[2]) as archive:
        for folder, stem in folders.items():
            names = sorted(name for name in archive.namelist()
                           if f'/{folder}/' in name and name.lower().endswith('.jpg'))
            if len(names) != 3:
                raise ValueError(f'Expected three photographs for {folder}, found {len(names)}')
            for i, name in enumerate(names, 1):
                filename = f'{stem}_{i:02}.jpg'
                (photo_dir / filename).write_bytes(archive.read(name))
                provenance[filename] = name
    (private / 'photo-sources.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')

real_tasks = [
    ('oreo', 'Oreo to Red Bowl', 'Pick up the Oreo and place it in the red bowl.'),
    ('chip', 'Poker Chip Selection', 'Select the chip whose value × 5 = 100.'),
    ('cake', 'Cake Stacking', 'Stack two cakes on a can of luncheon meat.'),
    ('glasses', 'Glasses Bridge Grasp', 'Lift the glasses at the bridge.'),
    ('towel', 'Towel Folding', 'Fold the towel.')]
real_gallery = []
for stem, title, instruction in real_tasks:
    photos = sorted(photo_dir.glob(f'{stem}_*.jpg'))
    if not photos:
        continue
    images = []
    for i, photo in enumerate(photos):
        stage = ['Initial Scene', 'Execution', 'Final Scene'][i] if len(photos) == 3 else f'Frame {i + 1}'
        url = f'assets/figures/real_robot/{photo.name}'
        images.append(f'<figure><img loading="lazy" src="{url}" alt="{title}: {stage}" width="1920" height="1080"><figcaption>{stage}</figcaption></figure>')
    real_gallery.append(f'<details class="real-task"{" open" if not real_gallery else ""}><summary><span class="task-index">{len(real_gallery) + 1:02}</span><span><h3>{title}</h3><p>{instruction}</p></span><span class="expand-icon" aria-hidden="true">+</span></summary><div class="real-photos">{"".join(images)}</div></details>')
real_gallery = '<div class="real-gallery">' + ''.join(real_gallery) + '</div>'


def table_rows(label):
    start = tex.index('\\label{' + label + '}')
    body = tex[start:tex.index('\\end{tabular}', start)]
    body = body[body.index('\\toprule') + len('\\toprule'):]
    rows = []
    for line in body.splitlines():
        if '&' not in line:
            continue
        line = re.sub(r'\\rule\[[^\]]*\]\{[^}]*\}\{[^}]*\}', '', line)
        line = line.replace(r'\highlightrowstrut', '')
        cells = [plain(c).replace('EmbodiedEvo', 'EmbodiedRSI') for c in line.split(r'\\')[0].split('&')]
        rows.append(cells)
    return rows


def table(label, caption):
    rows = []
    for cells in table_rows(label):
        tag = 'th' if not rows else 'td'
        highlight = ' class="ours"' if any('EmbodiedRSI' in c for c in cells) or ('Overall' in cells and rows) else ''
        cells_html = ''.join(f'<{tag}>{c}</{tag}>' for c in cells)
        rows.append(f'<tr{highlight}>{cells_html}</tr>')
    return f'<div class="table-wrap" tabindex="0" role="region" aria-label="{caption}"><table><caption>{caption}</caption><thead>{rows[0]}</thead><tbody>{"".join(rows[1:])}</tbody></table></div>'


def benchmark_chart(label, metric, title, identifier):
    source_rows = table_rows(label)
    column = source_rows[0].index(metric)
    data = [{'method': html.unescape(row[0]).replace(' (Ours)', ''),
             'success_rate': float(row[column])} for row in source_rows[1:]]
    assert all(0 <= row['success_rate'] <= 100 for row in data)
    data.sort(key=lambda row: row['success_rate'], reverse=True)
    ours = next(row['success_rate'] for row in data if row['method'] == 'EmbodiedRSI')
    best_baseline = max(row['success_rate'] for row in data if row['method'] != 'EmbodiedRSI')
    bars = []
    for row in data:
        method, value = html.escape(row['method']), row['success_rate']
        focal = ' focal' if row['method'] == 'EmbodiedRSI' else ''
        bars.append(f'<li class="bar-row{focal}" data-method="{method}" data-value="{value:.1f}"><span class="bar-label">{method}</span><span class="bar-track" aria-hidden="true"><span class="bar-fill" style="width:{value:.1f}%"></span></span><span class="bar-value">{value:.1f}%</span></li>')
    chart_data = {'benchmark': title, 'metric': metric, 'unit': 'percent',
                  'source': {'file': 'iclr2027_conference.tex', 'table_label': label}, 'rows': data}
    (private / f'{identifier}.json').write_text(json.dumps(chart_data, ensure_ascii=False, indent=2) + '\n')
    scope = 'Composite-Unseen' if metric == 'Composite-Unseen' else 'Overall'
    return f'<figure class="benchmark-chart" id="{identifier}" aria-labelledby="{identifier}-title"><div class="chart-heading"><div><h3 id="{identifier}-title">{title}</h3><p>{scope} · Success Rate (%)</p></div><div class="chart-highlight"><strong>{ours:.1f}<span>%</span></strong><span class="chart-delta">+{ours - best_baseline:.1f} pp vs. best baseline</span></div></div><ol class="bar-chart">{"".join(bars)}</ol><div class="chart-axis" aria-hidden="true"><span>0</span><span>25</span><span>50</span><span>75</span><span>100%</span></div></figure>'


def figure(name, alt, caption):
    return f'<figure><img src="assets/figures/{name}.png" alt="{alt}" loading="lazy" width="1200"><figcaption>{caption}</figcaption></figure>'

tasks = [
 ('atomic_seen__PickPlaceCounterToCabinet__robot0_agentview_left.png','Counter to Cabinet','Atomic-Seen'),
 ('atomic_seen__TurnOnMicrowave__robot0_agentview_left.png','Turn On Microwave','Atomic-Seen'),
 ('composite_seen__LoadDishwasher__robot0_agentview_left.png','Load Dishwasher','Composite-Seen'),
 ('composite_seen__PrepareCoffee__robot0_agentview_left.png','Prepare Coffee','Composite-Seen'),
 ('composite_unseen__ArrangeTea__robot0_agentview_left.png','Arrange Tea','Composite-Unseen'),
 ('composite_unseen__MakeIceLemonade__robot0_agentview_left.png','Make Ice Lemonade','Composite-Unseen')]
task_grid = ''.join(f'<figure class="task"><img loading="lazy" src="assets/figures/{file}" alt="{name} in RoboCasa365"><figcaption><strong>{name}</strong><span>{suite}</span></figcaption></figure>' for file,name,suite in tasks)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="EmbodiedRSI: a self-evolving agentic harness for continual robot learning through hypothesis-guided code and skill co-evolution.">
<meta name="theme-color" content="#26233e">
<title>EmbodiedRSI | Continual Robot Learning</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav aria-label="Main navigation"><a class="brand" href="#top">EmbodiedRSI</a><div><a href="#abstract">Abstract</a><a href="#method">Method</a><a href="#results">Results</a><a href="#real-world">Real-world</a></div></nav>
<main id="top">
<header class="hero">
<div class="hero-copy">
<p class="eyebrow">CONTINUAL ROBOT LEARNING</p>
<h1><span class="wordmark">Embodied<span class="wordmark-accent">RSI</span></span><span class="paper-title">Continual Robot Learning<br>Through Hypothesis-Guided Co-Evolution</span></h1>
{hero_identity}
<p class="subtitle">Building the recursive self-improvement layer for robotics: an agentic harness that evolves its own code, skills, and memory through physical experience.</p>
</div>
<div class="hero-media" aria-label="Real robot experiments"><figure class="hero-photo primary-photo"><img src="assets/figures/real_robot/glasses_03.jpg" alt="SO-101 robot lifting glasses at the bridge" width="1920" height="1080"><figcaption>Glasses Bridge Grasp</figcaption></figure><figure class="hero-photo secondary-photo"><img src="assets/figures/real_robot/cake_03.jpg" alt="SO-101 robot stacking cakes on a can of luncheon meat" width="1920" height="1080"><figcaption>Cake Stacking</figcaption></figure><span class="orbit orbit-one" aria-hidden="true"></span><span class="orbit orbit-two" aria-hidden="true"></span></div>
</header>
<div class="metrics"><div><strong>77.0<span>%</span></strong><p>RoboCasa365 overall</p></div><div><strong>86.8<span>%</span></strong><p>LIBERO-Pro overall</p></div><div><strong>71.3<span>%</span></strong><p>Zero-shot real-robot transfer</p></div></div>

<section id="overview" class="overview">{figure('overview','EmbodiedRSI architecture showing the Fast System, Hypothesis Graph, and Slow System memory','The Fast System uses a Hypothesis Graph to choose each physical experiment. Each result guides a joint code-skill update. The Slow System retains memories that improve later adaptation.')}</section>
<section id="abstract" class="abstract-section"><div class="section-label"><p class="eyebrow">THE PAPER</p><h2>Abstract</h2></div><p class="abstract">{abstract}</p></section>
<section id="method"><p class="eyebrow">FROM INTERACTION TO IMPROVEMENT</p><h2>Hypothesis-Guided Co-Evolution</h2>
<div class="cards"><article><span class="number">01</span><h3>Choose Informative Experiments</h3><p>The Fast System maintains competing code and skill hypotheses. Value-of-Information Experiment Selection prioritizes physical trials by expected uncertainty reduction relative to their cost.</p></article><article><span class="number">02</span><h3>Evolve Code and Skills Together</h3><p>Matched trials compare joint code-skill execution with each component from the same initial states. The Hypothesis Graph retains refinement history and relations supported by positive joint gain.</p></article><article><span class="number">03</span><h3>Learn What to Remember</h3><p>The Slow System builds Hierarchical Memory from execution records, hypotheses, and reusable cognition. Reward-Grounded Memory Learning selects memory actions based on later Fast-System improvement.</p></article></div>
{figure('hypothesis-graph','Hypothesis Graph before and after physical trials','Before experiments, dashed links mark code-skill relations awaiting evidence. After experiments, solid works-with edges identify relations supported by measured positive joint gain.')}
</section>
<section id="results"><p class="eyebrow">GENERALIZATION IN SIMULATION</p><h2>New Compositions. Changed Scenes.</h2><p>With the robot foundation model frozen, EmbodiedRSI reaches 71.3% success on RoboCasa365 Composite-Unseen, compared with 40.1% for Harness VLA. LIBERO-Pro evaluates instruction-redirection (T) and position-swap (S) perturbations.</p><div class="task-grid">{task_grid}</div>
<div class="benchmark-tabs" role="tablist" aria-label="Simulation benchmarks"><button id="tab-robocasa" type="button" role="tab" aria-selected="true" aria-controls="panel-robocasa">RoboCasa365 <span>Composite-Unseen</span></button><button id="tab-libero" type="button" role="tab" aria-selected="false" aria-controls="panel-libero" tabindex="-1">LIBERO-Pro <span>Overall</span></button></div>
<div class="benchmark-panels"><div id="panel-robocasa" role="tabpanel" aria-labelledby="tab-robocasa">{benchmark_chart('tab:main-results','Composite-Unseen','RoboCasa365','robocasa-unseen')}</div><div id="panel-libero" role="tabpanel" aria-labelledby="tab-libero">{benchmark_chart('tab:libero-results','Overall','LIBERO-Pro','libero-overall')}</div></div>
<p class="note">Simulation evaluation: 10 random seeds and 10 trials per seed for each task. Evolution and evaluation use mutually disjoint seeds.</p>
</section>
<section id="real-world"><p class="eyebrow">ZERO-SHOT SIM-TO-REAL TRANSFER</p><h2>From Simulated Experience to a Physical Robot</h2><p>The simulation-evolved agentic harness transfers to a physical SO-101 arm with a frozen SmolVLA backbone. Overall success rises from 46.0% to 71.3% across five tasks spanning multi-step manipulation, semantic and arithmetic reasoning, and precision grasping.</p>
{real_gallery}
{table('tab:real-robot-results','Real-Robot Success Rates: 30 Trials per Task')}
<p class="note">SmolVLA is fine-tuned before evaluation using 50 teleoperated demonstrations per task, then remains frozen during all trials. The agentic harness transfers zero-shot from simulation. Success on glasses bridge grasp falls from 60.0% to 56.7%.</p>
</section>
</main>
<footer><p>EmbodiedRSI · Continual Robot Learning through Hypothesis-Guided Co-Evolution</p><p><a href="#top">Back to top ↑</a></p></footer>
<script src="site.js" defer></script>
</body></html>
'''
(root / 'index.html').write_text(page)
print('Built index.html; abstract retained verbatim with LaTeX formatting converted to HTML.')
