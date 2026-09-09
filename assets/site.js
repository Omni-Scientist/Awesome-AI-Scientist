(function () {
  'use strict';

  var root = document.documentElement;
  var STORE = 'aais-theme';

  /* Each block is isolated: one failure must not take the rest of the page down. */
  function guard(name, fn) {
    try { fn(); } catch (err) {
      if (window.console) console.error('[' + name + ']', err);
    }
  }

  guard('theme', function () {
    var saved = null;
    try { saved = localStorage.getItem(STORE); } catch (e) { /* private mode */ }
    if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);

    var btn = document.getElementById('theme');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var dark = getComputedStyle(root).colorScheme.indexOf('dark') === 0;
      var next = dark ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(STORE, next); } catch (e) { /* ignore */ }
    });
  });

  var wired = [];

  /* Scoped so a single-file build with several routes in one DOM filters
     only the route the reader is looking at. */
  function initListing(scope, syncUrl) {
    if (wired.indexOf(scope) !== -1) return;
    wired.push(scope);
    var input = scope.querySelector('[data-role="q"]');
    var cards = [].slice.call(scope.querySelectorAll('.card'));
    if (!cards.length) return;

    var grids = [].slice.call(scope.querySelectorAll('.grid'));
    var groups = [].slice.call(scope.querySelectorAll('[data-group]'));
    var countEl = scope.querySelector('[data-role="count"]');
    var emptyEl = scope.querySelector('[data-role="empty"]');
    var yearSel = scope.querySelector('[data-role="year"]');
    var sortSel = scope.querySelector('[data-role="sort"]');
    var total = cards.length;
    var order = grids.map(function (g) { return [].slice.call(g.children); });

    function terms() {
      var v = input ? input.value.toLowerCase().trim() : '';
      return v ? v.split(/\s+/) : [];
    }

    function apply() {
      var words = terms();
      var wantYear = yearSel ? yearSel.value : '';
      var shown = 0;

      for (var i = 0; i < cards.length; i++) {
        var el = cards[i], ok = true;
        if (ok && wantYear && el.dataset.year !== wantYear) ok = false;
        if (ok && words.length) {
          var hay = el.dataset.s || '';
          for (var w = 0; w < words.length && ok; w++) {
            if (hay.indexOf(words[w]) === -1) ok = false;
          }
        }
        el.classList.toggle('is-hidden', !ok);
        if (ok) shown++;
      }

      for (var g = 0; g < groups.length; g++) {
        var live = groups[g].querySelectorAll('.card:not(.is-hidden)').length;
        groups[g].classList.toggle('is-hidden', live === 0);
        var badge = groups[g].querySelector('[data-live]');
        if (badge) {
          badge.textContent = live === Number(badge.dataset.live)
            ? badge.dataset.live : live + '/' + badge.dataset.live;
        }
      }

      if (countEl) {
        countEl.textContent = shown === total ? total + ' entries' : shown + ' of ' + total;
      }
      if (emptyEl) emptyEl.style.display = shown === 0 ? 'block' : 'none';

      if (input && syncUrl) {
        var q = input.value.trim();
        try {
          history.replaceState(null, '',
            location.pathname + (q ? '?q=' + encodeURIComponent(q) : '') + location.hash);
        } catch (e) { /* file:// */ }
      }
    }

    function resort() {
      var mode = sortSel ? sortSel.value : 'default';
      grids.forEach(function (grid, gi) {
        var kids = order[gi].slice();
        if (mode === 'stars') {
          kids.sort(function (a, b) {
            return (Number(b.dataset.stars) || -1) - (Number(a.dataset.stars) || -1);
          });
        } else if (mode === 'year') {
          kids.sort(function (a, b) {
            return (Number(b.dataset.year) || 0) - (Number(a.dataset.year) || 0);
          });
        } else if (mode === 'title') {
          kids.sort(function (a, b) {
            return a.dataset.title < b.dataset.title ? -1 : a.dataset.title > b.dataset.title ? 1 : 0;
          });
        }
        kids.forEach(function (k) { grid.appendChild(k); });
      });
    }

    var timer;
    if (input) {
      input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(apply, 90);
      });
      var seed = syncUrl ? new URLSearchParams(location.search).get('q') : null;
      if (seed) input.value = seed;
    }
    if (yearSel) yearSel.addEventListener('change', apply);
    if (sortSel) sortSel.addEventListener('change', resort);

    document.addEventListener('keydown', function (ev) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
      if (ev.key === '/' && !typing && input) { ev.preventDefault(); input.focus(); input.select(); }
      if (ev.key === 'Escape' && input && document.activeElement === input) {
        input.value = ''; apply(); input.blur();
      }
    });

    apply();
  }

  window.__aaisListing = function (scope) { guard('listing', function () { initListing(scope, false); }); };
  guard('listing', function () { initListing(document, true); });

  guard('cite', function () {
    var btn = document.getElementById('copycite');
    var pre = document.getElementById('cite');
    if (!btn || !pre) return;
    btn.addEventListener('click', function () {
      var done = function () {
        var was = btn.textContent;
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = was; }, 1400);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(pre.textContent).then(done, function () {});
      else done();
    });
  });
})();
