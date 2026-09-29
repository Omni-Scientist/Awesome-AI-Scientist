(function () {
  const DATA = JSON.parse(document.getElementById('data').textContent);
  const ALL = DATA.entries;
  const SECS = DATA.sections;
  const SEC = Object.fromEntries(SECS.map((s) => [s.key, s]));
  const GRP = {};
  SECS.forEach((s) => s.groups.forEach((g) => { GRP[s.key + '/' + g.key] = g; }));
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };
  const motion = !matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- icons
  const I = {
    star: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 .9l2.1 4.4 4.8.6-3.5 3.3.9 4.8L8 11.7 3.7 14l.9-4.8L1.1 5.9l4.8-.6Z"/></svg>',
    gh: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>',
    doc: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><path d="M3.5 1.5h6l3 3v10h-9z"/><path d="M9.5 1.5v3h3M5.8 8.2h4.4M5.8 11h4.4"/></svg>',
    hf: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="8" cy="8" r="6.4"/><path d="M5.2 9.6c.8 1.2 1.7 1.8 2.8 1.8s2-.6 2.8-1.8"/><circle cx="5.8" cy="6.4" r=".6" fill="currentColor"/><circle cx="10.2" cy="6.4" r=".6" fill="currentColor"/></svg>',
    web: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="8" cy="8" r="6.4"/><path d="M1.6 8h12.8M8 1.6c2 2.2 2 10.6 0 12.8M8 1.6c-2 2.2-2 10.6 0 12.8"/></svg>',
  };

  // ---------- state
  const colKey = () => 'ais-cols-' + (innerWidth < 640 ? 'm' : innerWidth < 1100 ? 't' : 'd');
  const state = {
    q: '', sec: '', grp: '', sort: store.get('ais-sort', 'curated'),
    cols: store.get(colKey(), innerWidth < 640 ? 1 : Math.max(2, Math.min(5, Math.round(innerWidth / 470)))),
    seed: Math.random(),
  };
  const hay = new Map(ALL.map((c) => [c.k, [c.n, c.s, c.v, c.rp, c.ax, SEC[c.sec].label, (GRP[c.sec + '/' + c.g] || {}).label, c.d].join('\n').toLowerCase()]));

  // ---------- helpers
  function rng(seed) { let s = Math.floor(seed * 2 ** 31) || 1; return () => { s = (s * 48271) % 2147483647; return s / 2147483647; }; }
  const kstars = (n) => n >= 10000 ? Math.round(n / 1000) + 'k' : n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n);
  const domain = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return ''; } };
  const pad = (n) => String(n).padStart(3, '0');

  function cardHTML(c, eager) {
    const s = SEC[c.sec], g = GRP[c.sec + '/' + c.g];
    const cls = ['card'];
    if (c.st >= 1000) cls.push('holo');
    const art = c.img
      ? `<div class="art fit-${c.fit}"><img ${eager ? '' : 'loading="lazy" '}decoding="async" src="${esc(c.img)}" width="${c.w}" height="${c.h}" alt=""></div>`
      : `<div class="art none" aria-hidden="true"><span>${esc(c.n)}</span><em>${s.icon}</em></div>`;
    const links = [];
    const add = (href, title, icon) => { if (href && href !== c.u && !links.some((l) => l.includes(`href="${esc(href)}"`))) links.push(`<a href="${esc(href)}" target="_blank" rel="noopener" title="${title}" aria-label="${title}: ${esc(c.n)}">${icon}</a>`); };
    if (c.ax) add('https://arxiv.org/abs/' + c.ax, 'Paper', I.doc);
    if (c.rp) add('https://github.com/' + c.rp, 'Code', I.gh);
    if (c.hf) add(c.hf, 'Hugging Face', I.hf);
    if (c.web) add(c.web, 'Website', I.web);
    const year = c.d ? c.d.slice(0, 4) : '';
    let who;
    if (c.v) who = `<span class="vn" title="${esc(c.v)}">${esc(c.v)}</span>`;
    else if (c.rp) who = `<span class="who">${c.av ? `<img src="${esc(c.av)}" alt="" loading="lazy" width="24" height="24">` : ''}<span>${esc(c.rp.split('/')[0])}</span></span>`;
    else if (c.ax) who = `<span class="vn">arXiv</span>${year ? `<span class="yr">${year}</span>` : ''}`;
    else who = `<span class="who"><span>${esc(domain(c.u))}</span></span>`;
    return `<article class="${cls.join(' ')}" style="--c:var(--s-${c.sec});--on:var(--on-${c.sec})" data-k="${esc(c.k)}">
  <div class="band"><span class="em" aria-hidden="true">${s.icon}</span><span class="no"><small>No.</small>${pad(c.o + 1)}</span>${g ? `<span class="g">${esc(g.label)}</span>` : ''}${c.st ? `<span class="st" title="${c.st.toLocaleString('en')} GitHub stars">${I.star}${kstars(c.st)}</span>` : ''}</div>
  ${art}
  <h3 class="nm"><a href="${esc(c.u)}" target="_blank" rel="noopener">${esc(c.n)}</a></h3>
  <p class="tx">${esc(c.s)}</p>
  <div class="ft">${who}<span class="lk">${links.join('')}</span></div>
</article>`;
  }

  function chapHTML(s, n) {
    return `<div class="chap" style="--c:var(--s-${s.key});--on:var(--on-${s.key})"><span class="ep">${String(s.ep).padStart(2, '0')}</span>
  <h2>${esc(s.label)} <small>${n} cards</small></h2><p>${esc(s.intro)}</p><span class="kj" aria-hidden="true">${s.icon}</span></div>`;
  }
  function subHTML(s, g, n) {
    return `<div class="chap sub" style="--c:var(--s-${s.key});--on:var(--on-${s.key})"><h2>${esc(g.label)} <small>${n}</small></h2><p>${esc(g.intro)}</p></div>`;
  }

  // ---------- filter + sort
  let shown = [];
  function compute() {
    const terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    let list = ALL.filter((c) => (!state.sec || c.sec === state.sec) && (!state.grp || c.g === state.grp)
      && (!terms.length || terms.every((w) => hay.get(c.k).includes(w))));
    if (state.sort === 'random') { const r = rng(state.seed); list = list.map((c) => [r(), c]).sort((a, b) => a[0] - b[0]).map((x) => x[1]); }
    else if (state.sort === 'stars') list = list.slice().sort((a, b) => ((b.st || 0) - (a.st || 0)) || (a.o - b.o));
    else if (state.sort === 'newest') list = list.slice().sort((a, b) => ((b.d || '').localeCompare(a.d || '')) || (a.o - b.o));
    shown = list;
  }
  function render() {
    compute();
    const grid = $('#grid');
    grid.style.setProperty('--cols', state.cols);
    const chapters = state.sort === 'curated' && !state.q && !state.grp;
    let html = '', last = null, eager = 0;
    for (const c of shown) {
      if (chapters) {
        const key = state.sec ? c.g : c.sec;
        if (key !== last) {
          last = key;
          if (state.sec) { const g = GRP[c.sec + '/' + c.g]; html += subHTML(SEC[c.sec], g, g.n); }
          else html += chapHTML(SEC[c.sec], SEC[c.sec].n);
        }
      }
      html += cardHTML(c, eager++ < 6);
    }
    grid.innerHTML = html;
    compact();
    $('#empty').hidden = shown.length > 0;
    $('#count').textContent = shown.length === ALL.length ? `${ALL.length} cards` : `${shown.length} of ${ALL.length}`;
    $$('#sort button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.sort === state.sort)));
  }
  function compact() {
    const grid = $('#grid');
    grid.classList.toggle('compact', grid.clientWidth / state.cols < 300);
  }
  function syncUrl() {
    const p = new URLSearchParams();
    if (state.sec) p.set('sec', state.sec);
    if (state.grp) p.set('grp', state.grp);
    if (state.q) p.set('q', state.q);
    const qs = p.toString();
    history.replaceState(null, '', qs ? '?' + qs : location.pathname);
  }
  function pressTabs() {
    $$('#tabs .tab').forEach((t) => t.setAttribute('aria-pressed', String(t.dataset.sec === state.sec)));
    const box = $('#groups');
    if (!state.sec) { box.hidden = true; box.innerHTML = ''; return; }
    const s = SEC[state.sec];
    box.hidden = false;
    box.innerHTML = `<button type="button" class="chip" data-grp="" aria-pressed="${!state.grp}">All ${esc(s.label)}<b>${s.n}</b></button>` +
      s.groups.map((g) => `<button type="button" class="chip" data-grp="${g.key}" aria-pressed="${state.grp === g.key}">${esc(g.label)}<b>${g.n}</b></button>`).join('');
  }

  // ---------- controls
  $('#tabs').addEventListener('click', (e) => {
    const b = e.target.closest('.tab'); if (!b) return;
    state.sec = (b.dataset.sec === state.sec) ? '' : b.dataset.sec;
    state.grp = '';
    pressTabs(); syncUrl(); render();
  });
  $('#groups').addEventListener('click', (e) => {
    const b = e.target.closest('.chip'); if (!b) return;
    state.grp = b.dataset.grp === state.grp ? '' : b.dataset.grp;
    pressTabs(); syncUrl(); render();
  });
  // the coloured strip under the header opens a section without a page load
  $$('.spectrum a').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    state.sec = a.dataset.sec; state.grp = '';
    pressTabs(); syncUrl(); render();
    $('#wall').scrollIntoView({ behavior: motion ? 'smooth' : 'auto' });
  }));
  let qT;
  $('#q').addEventListener('input', (e) => { clearTimeout(qT); qT = setTimeout(() => { state.q = e.target.value.trim(); syncUrl(); render(); }, 140); });
  $('#sort').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.sort === 'random' && state.sort === 'random') state.seed = Math.random();
    state.sort = b.dataset.sort; store.set('ais-sort', state.sort); render();
  });
  const applyCols = () => { $('#colN').textContent = state.cols; store.set(colKey(), state.cols); render(); };
  $('#colDec').addEventListener('click', () => { state.cols = Math.max(1, state.cols - 1); applyCols(); });
  $('#colInc').addEventListener('click', () => { state.cols = Math.min(6, state.cols + 1); applyCols(); });
  let rT; addEventListener('resize', () => { clearTimeout(rT); rT = setTimeout(compact, 120); });

  // ---------- theme
  const root = document.documentElement, tb = $('#theme');
  const theme = () => root.getAttribute('data-theme') || 'light';
  const label = () => tb.setAttribute('aria-label', theme() === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  label();
  tb.addEventListener('click', () => { const t = theme() === 'dark' ? 'light' : 'dark'; root.setAttribute('data-theme', t); store.set('ais-theme', t); label(); });

  // ---------- keyboard: / focuses search
  document.addEventListener('keydown', (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (e.key === 'Escape' && typing) { document.activeElement.blur(); return; }
    if (e.key === '/' && !typing) { e.preventDefault(); $('#q').focus({ preventScroll: true }); $('#q').scrollIntoView({ block: 'center', behavior: motion ? 'smooth' : 'auto' }); $('#q').select(); }
  });

  // ---------- back to top
  const up = $('#up');
  addEventListener('scroll', () => up.classList.toggle('on', scrollY > 900), { passive: true });
  up.addEventListener('click', () => scrollTo({ top: 0, behavior: motion ? 'smooth' : 'auto' }));

  // ---------- init
  const p = new URLSearchParams(location.search);
  if (p.get('q')) { $('#q').value = p.get('q'); state.q = p.get('q').trim(); }
  if (SEC[p.get('sec')]) state.sec = p.get('sec');
  if (state.sec && GRP[state.sec + '/' + p.get('grp')]) state.grp = p.get('grp');
  if (!['curated', 'stars', 'newest', 'random'].includes(state.sort)) state.sort = 'curated';
  $('#colN').textContent = state.cols;
  pressTabs();
  render();
})();
