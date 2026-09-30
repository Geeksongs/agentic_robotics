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
figures = root / 'assets/figures'
figures.mkdir(parents=True, exist_ok=True)
(root / 'assets/paper').mkdir(parents=True, exist_ok=True)

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
shutil.copy2(source / 'iclr2027_conference.pdf', root / 'assets/paper/embodied-evo.pdf')

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
    (photo_dir / 'sources.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')

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
        images.append(f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{title}: {stage}" width="1920" height="1080"></a><figcaption>{stage}</figcaption></figure>')
    real_gallery.append(f'<article class="real-task"><h3>{title}</h3><p>{instruction}</p><div class="real-photos">{"".join(images)}</div></article>')
real_gallery = '<div class="real-gallery">' + ''.join(real_gallery) + '</div>'


def table(label, caption):
    start = tex.index('\\label{' + label + '}')
    body = tex[start:tex.index('\\end{tabular}', start)]
    body = body[body.index('\\toprule') + len('\\toprule'):]
    rows = []
    for line in body.splitlines():
        if '&' not in line:
            continue
        line = re.sub(r'\\rule\[[^\]]*\]\{[^}]*\}\{[^}]*\}', '', line)
        line = line.replace(r'\highlightrowstrut', '')
        cells = [plain(c).replace('EmbodiedEvo', 'RoboGenesis') for c in line.split(r'\\')[0].split('&')]
        tag = 'th' if not rows else 'td'
        highlight = ' class="ours"' if 'EmbodiedEvo' in line or ('Overall' in line and rows) else ''
        cells_html = ''.join(f'<{tag}{" scope=\"col\"" if tag == "th" else ""}>{c}</{tag}>' for c in cells)
        rows.append(f'<tr{highlight}>{cells_html}</tr>')
    return f'<div class="table-wrap" tabindex="0" role="region" aria-label="{caption}"><table><caption>{caption}</caption><thead>{rows[0]}</thead><tbody>{"".join(rows[1:])}</tbody></table></div>'

def figure(name, alt, caption):
    return f'<figure><a href="assets/figures/{name}.png"><img src="assets/figures/{name}.png" alt="{alt}" loading="lazy" width="1200"></a><figcaption>{caption}</figcaption></figure>'

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
<meta name="description" content="RoboGenesis: a self-evolving agentic harness for continual robot learning through hypothesis-guided code and skill co-evolution.">
<meta name="theme-color" content="#243d83">
<title>RoboGenesis | Continual Robot Learning</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav aria-label="Main navigation"><a class="brand" href="#top">RoboGenesis</a><div><a href="#abstract">Abstract</a><a href="#method">Method</a><a href="#results">Results</a><a href="#real-world">Real-world</a></div></nav>
<main id="top">
<header class="hero">
<p class="eyebrow">CONTINUAL ROBOT LEARNING</p>
<h1><span>RoboGenesis</span><br>Continual Robot Learning<br>Through Hypothesis-Guided Co-Evolution</h1>
<div class="authors" aria-label="Authors"><span>Python Song<sup>1</sup></span>, <span>Zhixuan Liang<sup>2</sup></span>, <span>Kelsey Fu<sup>2</sup></span>, <span>Mengdi Wang<sup>2</sup></span>, <span>Junfeng Yang<sup>1</sup></span>, <span>Shilong Liu<sup>2</sup></span></div>
<div class="affiliations"><span><sup>1</sup> Columbia University</span><span><sup>2</sup> Princeton University</span></div>
<p class="subtitle">Building the recursive self-improvement layer for robotics: an agentic harness that evolves its own code, skills, and memory through physical experience.</p>
<div class="links"><a class="button primary" href="assets/paper/embodied-evo.pdf">Read the paper ↗</a><a class="button" href="https://github.com/Geeksongs/agentic_robotics">Website source ↗</a></div>
<div class="metrics"><div><strong>77.0<span>%</span></strong><p>RoboCasa365 overall</p></div><div><strong>86.8<span>%</span></strong><p>LIBERO-Pro overall</p></div><div><strong>71.3<span>%</span></strong><p>Zero-shot real-robot transfer</p></div></div>
</header>
<section id="overview" class="overview">{figure('overview','RoboGenesis architecture showing the Fast System, Hypothesis Graph, and Slow System memory','The Fast System uses a Hypothesis Graph to choose each physical experiment. Each result guides a joint code-skill update. The Slow System retains memories that improve later adaptation.')}</section>
<section id="abstract"><p class="eyebrow">THE PAPER</p><h2>Abstract</h2><p class="abstract">{abstract}</p></section>
<section id="method"><p class="eyebrow">FROM INTERACTION TO IMPROVEMENT</p><h2>Hypothesis-Guided Co-Evolution</h2>
<div class="cards"><article><span class="number">01</span><h3>Choose Informative Experiments</h3><p>The Fast System maintains competing code and skill hypotheses. Value-of-Information Experiment Selection prioritizes physical trials by expected uncertainty reduction relative to their cost.</p></article><article><span class="number">02</span><h3>Evolve Code and Skills Together</h3><p>Matched trials compare joint code-skill execution with each component from the same initial states. The Hypothesis Graph retains refinement history and relations supported by positive joint gain.</p></article><article><span class="number">03</span><h3>Learn What to Remember</h3><p>The Slow System builds Hierarchical Memory from execution records, hypotheses, and reusable cognition. Reward-Grounded Memory Learning selects memory actions based on later Fast-System improvement.</p></article></div>
{figure('hypothesis-graph','Hypothesis Graph before and after physical trials','Before experiments, dashed links mark code-skill relations awaiting evidence. After experiments, solid works-with edges identify relations supported by measured positive joint gain.')}
</section>
<section id="results"><p class="eyebrow">GENERALIZATION IN SIMULATION</p><h2>New Compositions. Changed Scenes.</h2><p>With the robot foundation model frozen, RoboGenesis reaches 71.3% success on RoboCasa365 Composite-Unseen, compared with 40.1% for Harness VLA. LIBERO-Pro evaluates instruction-redirection (T) and position-swap (S) perturbations.</p><div class="task-grid">{task_grid}</div>
{table('tab:main-results','RoboCasa365 Success Rates (%)')}
{table('tab:libero-results','LIBERO-Pro Success Rates (%); — / -- denotes a cell not applicable to the method')}
<p class="note">Simulation evaluation: 10 random seeds and 10 trials per seed for each task. Evolution and evaluation use mutually disjoint seeds.</p>
</section>
<section id="real-world"><p class="eyebrow">ZERO-SHOT SIM-TO-REAL TRANSFER</p><h2>From Simulated Experience to a Physical Robot</h2><p>The simulation-evolved agentic harness transfers to a physical SO-101 arm with a frozen SmolVLA backbone. Overall success rises from 46.0% to 71.3% across five tasks spanning multi-step manipulation, semantic and arithmetic reasoning, and precision grasping.</p>
{real_gallery}
{table('tab:real-robot-results','Real-Robot Success Rates: 30 Trials per Task')}
<p class="note">SmolVLA is fine-tuned before evaluation using 50 teleoperated demonstrations per task, then remains frozen during all trials. The agentic harness transfers zero-shot from simulation. Success on glasses bridge grasp falls from 60.0% to 56.7%.</p>
</section>
</main>
<footer><p>RoboGenesis · Continual Robot Learning through Hypothesis-Guided Co-Evolution</p><p><a href="assets/paper/embodied-evo.pdf">Paper</a> · <a href="https://github.com/Geeksongs/agentic_robotics">Website source</a> · <a href="#top">Back to top ↑</a></p><p class="credit">Website adapted from the <a href="https://github.com/Geeksongs/realtime-robosuite/tree/website">Realtime Robosuite website branch</a>. Content and figures from the EmbodiedEvo manuscript.</p></footer>
</body></html>
'''
(root / 'index.html').write_text(page)
print('Built index.html; abstract retained verbatim with LaTeX formatting converted to HTML.')
