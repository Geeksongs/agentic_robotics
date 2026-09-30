const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectTab(selected, focus = false) {
  for (const tab of tabs) {
    const active = tab === selected;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
  }
  if (focus) selected.focus();
}
for (const [index, tab] of tabs.entries()) {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectTab(tabs[next], true); }
  });
}
if (tabs.length) selectTab(tabs[0]);
// Open a benchmark directly through its stable section link.
function followChartLink() {
  if (location.hash === '#libero-overall') selectTab(document.getElementById('tab-libero'));
  if (location.hash === '#robocasa-unseen') selectTab(document.getElementById('tab-robocasa'));
}
followChartLink();
window.addEventListener('hashchange', followChartLink);
const sections = [...document.querySelectorAll('main section[id]')];
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    for (const link of document.querySelectorAll('nav div a')) {
      if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }
}, {rootMargin: '-15% 0px -55% 0px'});
sections.forEach(section => observer.observe(section));
