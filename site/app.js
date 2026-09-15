(function () {
  'use strict';

  var SECTIONS = window.YII_SECTIONS || [];
  var INDEX = window.YII_INDEX || [];
  var root = document.documentElement;
  var body = document.body;
  var qInput = document.getElementById('q');
  var resultsBox = document.getElementById('results');
  var navButtons = [].slice.call(document.querySelectorAll('.nav-item'));
  var sections = [].slice.call(document.querySelectorAll('.doc > section'));
  var rail = document.getElementById('rail');
  var allBtn = document.getElementById('all-btn');
  var themeBtn = document.getElementById('theme-btn');
  var menuBtn = document.getElementById('menu-btn');
  var scrim = document.getElementById('scrim');
  var allMode = false;

  INDEX.forEach(function (e) { e.xl = (e.t + ' ' + e.x).toLowerCase(); });

  /* ---------------- theme ---------------- */

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }
  function read(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  function applyTheme(mode) {
    if (mode === 'dark' || mode === 'light') {
      root.setAttribute('data-theme', mode);
    } else {
      root.removeAttribute('data-theme');
    }
    var dark = mode === 'dark' || (mode !== 'light' &&
      window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    themeBtn.setAttribute('aria-label', dark ? 'Светлая тема' : 'Тёмная тема');
    themeBtn.innerHTML = dark
      ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M20.5 14.3A8.8 8.8 0 1 1 9.7 3.5a7 7 0 0 0 10.8 10.8z"/></svg>';
  }

  applyTheme(read('yii-theme') || 'system');

  themeBtn.addEventListener('click', function () {
    var current = root.getAttribute('data-theme');
    var dark = current === 'dark' || (!current && window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    applyTheme(next);
    store('yii-theme', next);
  });

  /* ---------------- routing ---------------- */

  function sectionIndexById(id) {
    for (var i = 0; i < SECTIONS.length; i++) {
      if (SECTIONS[i].id === id) return i;
    }
    return -1;
  }

  function buildRail(idx) {
    if (!rail) return;
    var heads = [].slice.call(sections[idx].querySelectorAll('h2[id], h3[id]'));
    if (!heads.length) { rail.innerHTML = ''; return; }
    var html = '<div class="rail-label">На этой странице</div>';
    heads.forEach(function (h) {
      var text = h.getAttribute('data-title') || h.textContent.replace('#', '').trim();
      html += '<a href="#' + h.id + '" class="' + (h.tagName === 'H3' ? 'lvl3' : '') + '">' +
        escapeHtml(text) + '</a>';
    });
    rail.innerHTML = html;
  }

  function show(idx, anchor, push) {
    if (idx < 0 || idx >= sections.length) idx = 0;
    if (!allMode) {
      sections.forEach(function (s, i) { s.hidden = i !== idx; });
    }
    navButtons.forEach(function (b, i) {
      if (i === idx) { b.setAttribute('aria-current', 'true'); }
      else { b.removeAttribute('aria-current'); }
    });
    buildRail(idx);
    document.title = SECTIONS[idx].title + ' — Шпаргалка Yii2';

    var hash = '#' + (anchor || SECTIONS[idx].id);
    if (push !== false && location.hash !== hash) {
      history.replaceState(null, '', hash);
    }

    if (anchor) {
      var target = document.getElementById(anchor);
      if (target) {
        var top = target.getBoundingClientRect().top + window.pageYOffset - 76;
        window.scrollTo({ top: top, behavior: 'auto' });
        return;
      }
    }
    window.scrollTo({ top: 0, behavior: 'auto' });
  }

  function resolveHash(push) {
    var raw = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    if (!raw) { show(0, null, push); return; }
    var byId = sectionIndexById(raw);
    if (byId >= 0) { show(byId, null, push); return; }
    var el = document.getElementById(raw);
    if (el) {
      var host = el.closest('section[data-sec]');
      var idx = host ? sectionIndexById(host.getAttribute('data-sec')) : 0;
      show(idx, raw, push);
      return;
    }
    show(0, null, push);
  }

  navButtons.forEach(function (btn, i) {
    btn.addEventListener('click', function () {
      closeNav();
      show(i);
    });
  });

  window.addEventListener('hashchange', function () { resolveHash(false); });

  /* jump links inside the document */
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    if (!id) return;
    var target = document.getElementById(id);
    var idx = sectionIndexById(id);
    if (idx >= 0) { e.preventDefault(); show(idx); return; }
    if (target) {
      e.preventDefault();
      var host = target.closest('section[data-sec]');
      show(host ? sectionIndexById(host.getAttribute('data-sec')) : 0, id);
    }
  });

  /* ---------------- "all sections" mode ---------------- */

  allBtn.addEventListener('click', function () {
    allMode = !allMode;
    allBtn.setAttribute('aria-pressed', allMode ? 'true' : 'false');
    body.classList.toggle('all-mode', allMode);
    if (allMode) {
      sections.forEach(function (s) { s.hidden = false; });
    } else {
      resolveHash(false);
    }
  });

  /* ---------------- mobile nav ---------------- */

  function closeNav() { body.classList.remove('nav-open'); }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { body.classList.toggle('nav-open'); });
  }
  if (scrim) scrim.addEventListener('click', closeNav);

  /* ---------------- search ---------------- */

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function highlight(text, terms) {
    var out = escapeHtml(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
    });
    return out;
  }

  function snippet(text, terms) {
    var low = text.toLowerCase();
    var pos = -1;
    for (var i = 0; i < terms.length; i++) {
      var p = low.indexOf(terms[i]);
      if (p >= 0 && (pos < 0 || p < pos)) pos = p;
    }
    var start = Math.max(0, pos - 45);
    var cut = text.slice(start, start + 190).trim();
    return (start > 0 ? '…' : '') + cut + (start + 190 < text.length ? '…' : '');
  }

  var hits = [];
  var cursor = -1;

  function search(query) {
    var terms = query.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return [];
    var scored = [];
    for (var i = 0; i < INDEX.length; i++) {
      var e = INDEX[i];
      var title = e.t.toLowerCase();
      var text = e.xl;
      var score = 0, ok = true;
      for (var j = 0; j < terms.length; j++) {
        var t = terms[j];
        var inTitle = title.indexOf(t);
        var inText = text.indexOf(t);
        if (inTitle < 0 && inText < 0) { ok = false; break; }
        if (inTitle === 0) score += 60;
        else if (inTitle > 0) score += 34;
        if (inText >= 0) score += 8;
      }
      if (!ok) continue;
      if (e.d === 2) score += 4;
      scored.push({ e: e, score: score });
    }
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 24).map(function (s) { return s.e; });
  }

  function renderResults(query) {
    var terms = query.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!hits.length) {
      resultsBox.innerHTML = '<div class="results-empty">Ничего не найдено по запросу «' +
        escapeHtml(query) + '». Попробуйте имя класса или метода, например <code>joinWith</code>.</div>';
      resultsBox.hidden = false;
      return;
    }
    var html = '';
    hits.forEach(function (e, i) {
      html += '<button type="button" class="res' + (i === cursor ? ' is-active' : '') +
        '" data-i="' + i + '">' +
        '<span class="res-top">' + escapeHtml(SECTIONS[e.s].num + ' · ' + SECTIONS[e.s].title) + '</span>' +
        '<span class="res-title">' + highlight(e.t, terms) + '</span>' +
        '<span class="res-snip">' + highlight(snippet(e.x, terms), terms) + '</span>' +
        '</button>';
    });
    resultsBox.innerHTML = html;
    resultsBox.hidden = false;
  }

  function closeResults() {
    resultsBox.hidden = true;
    resultsBox.innerHTML = '';
    cursor = -1;
    hits = [];
  }

  function gotoHit(hit) {
    closeResults();
    qInput.blur();
    show(hit.s, hit.a);
  }

  var debounce;
  qInput.addEventListener('input', function () {
    var value = qInput.value.trim();
    clearTimeout(debounce);
    if (value.length < 2) { closeResults(); return; }
    debounce = setTimeout(function () {
      hits = search(value);
      cursor = hits.length ? 0 : -1;
      renderResults(value);
    }, 90);
  });

  resultsBox.addEventListener('click', function (e) {
    var btn = e.target.closest('.res');
    if (!btn) return;
    gotoHit(hits[+btn.getAttribute('data-i')]);
  });

  qInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeResults(); qInput.blur(); return; }
    if (!hits.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      cursor = (cursor + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length;
      renderResults(qInput.value.trim());
      var active = resultsBox.querySelector('.res.is-active');
      if (active) active.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (cursor >= 0) gotoHit(hits[cursor]);
    }
  });

  document.addEventListener('click', function (e) {
    if (!resultsBox.hidden && !e.target.closest('.search')) closeResults();
  });

  document.addEventListener('keydown', function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) {
      e.preventDefault();
      qInput.focus();
      qInput.select();
    } else if (e.key === 'Escape') {
      closeNav();
      closeResults();
    }
  });

  /* ---------------- copy buttons ---------------- */

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.copy') : null;
    if (!btn) return;
    var pre = btn.closest('.code').querySelector('pre');
    var text = pre ? pre.innerText : '';
    var done = function () {
      var label = btn.querySelector('span');
      if (!label) return;
      var old = label.textContent;
      label.textContent = 'скопировано';
      btn.classList.add('done');
      setTimeout(function () { label.textContent = old; btn.classList.remove('done'); }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  });

  function fallbackCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (err) { /* nothing to do */ }
    document.body.removeChild(ta);
  }

  /* ---------------- rail highlight ---------------- */

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking || !rail) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var links = [].slice.call(rail.querySelectorAll('a'));
      if (!links.length) return;
      var best = null;
      links.forEach(function (link) {
        var el = document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
        if (!el) return;
        if (el.getBoundingClientRect().top - 110 <= 0) best = link;
      });
      links.forEach(function (l) { l.classList.remove('is-active'); });
      (best || links[0]).classList.add('is-active');
    });
  }, { passive: true });

  /* ---------------- syntax highlighting ---------------- */

  function highlightCode() {
    if (!window.hljs) return;
    [].slice.call(document.querySelectorAll('pre > code[data-lang]')).forEach(function (block) {
      var lang = block.getAttribute('data-lang');
      try {
        if (lang && window.hljs.getLanguage(lang)) {
          block.innerHTML = window.hljs.highlight(block.textContent, { language: lang }).value;
        } else {
          block.innerHTML = window.hljs.highlightAuto(block.textContent).value;
        }
        block.classList.add('hljs');
      } catch (err) { /* leave the code as plain text */ }
    });
  }

  highlightCode();
  resolveHash(false);
})();
