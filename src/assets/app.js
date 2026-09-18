/* Курс по Yii 2: клиентская логика (без зависимостей). */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var PAGE = body.getAttribute('data-page');
  var KEY_THEME = 'yii2:theme';
  var KEY_DONE = 'yii2:done';

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватный режим */ } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ------------------------------------------------------------ тема */
  var themeBtn = $('#theme-btn');
  function prefersDark() { return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches; }
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    return t === 'dark' || t === 'light' ? t : (prefersDark() ? 'dark' : 'light');
  }
  function applyTheme(t) {
    if (t === 'dark' || t === 'light') root.setAttribute('data-theme', t); else root.removeAttribute('data-theme');
    if (themeBtn) {
      var explicit = root.getAttribute('data-theme');
      themeBtn.title = 'Тема: ' + (explicit ? (explicit === 'dark' ? 'тёмная' : 'светлая') : 'системная') + ' — нажмите, чтобы переключить';
    }
  }
  applyTheme(load(KEY_THEME));
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    applyTheme(next); store(KEY_THEME, next);
  });

  /* ------------------------------------------------------------ прогресс */
  var PAGES = window.PAGE_LIST || [];
  function doneSet() {
    try { var a = JSON.parse(load(KEY_DONE) || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; }
  }
  function setDone(id, on) {
    var a = doneSet().filter(function (x) { return x !== id; });
    if (on) a.push(id);
    store(KEY_DONE, JSON.stringify(a));
    renderProgress();
  }
  function renderProgress() {
    var done = doneSet();
    var total = PAGES.length || 1;
    var pct = Math.round(done.length / total * 100);
    $$('[data-page]').forEach(function (el) {
      if (el === body) return;
      var id = el.getAttribute('data-page');
      var on = done.indexOf(id) >= 0;
      if (el.tagName === 'INPUT') el.checked = on; else el.classList.toggle('done', on);
    });
    var num = $('#progress-num'); if (num) num.textContent = pct;
    var ring = $('.ring-fg'); if (ring) ring.style.strokeDasharray = pct + ' 100';
    var pill = $('#progress-pill'); if (pill) pill.classList.toggle('has-progress', done.length > 0);
    var bar = $('#progress-bar'); if (bar) { bar.style.width = pct + '%'; bar.parentNode.setAttribute('aria-valuenow', pct); }
    var dn = $('#progress-done'); if (dn) dn.textContent = done.length;
    var cont = $('#continue-link');
    if (cont && PAGES.length) {
      var next = null;
      for (var i = 0; i < PAGES.length; i++) if (done.indexOf(PAGES[i].id) < 0) { next = PAGES[i]; break; }
      if (next) { cont.href = next.id + '.html'; cont.textContent = (done.length ? 'Продолжить: ' : 'Начать: ') + next.t + ' →'; }
      else { cont.href = 'cheatsheet.html'; cont.textContent = 'Всё изучено! Открыть памятку →'; }
    }
  }
  $$('.learned-box').forEach(function (box) {
    box.addEventListener('change', function () { setDone(box.getAttribute('data-page'), box.checked); });
  });
  var reset = $('#reset-progress');
  if (reset) reset.addEventListener('click', function () {
    if (confirm('Сбросить отметки об изученных разделах?')) { store(KEY_DONE, '[]'); renderProgress(); }
  });
  renderProgress();

  /* ------------------------------------------------------------ сайдбар (мобильный) */
  var sidebar = $('#sidebar'), menuBtn = $('#menu-btn'), scrim = $('#scrim');
  function openMenu(on) {
    if (!sidebar) return;
    sidebar.classList.toggle('open', on);
    body.classList.toggle('menu-open', on);
    if (menuBtn) menuBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
  }
  if (menuBtn) menuBtn.addEventListener('click', function () { openMenu(!sidebar.classList.contains('open')); });
  if (scrim) scrim.addEventListener('click', function () { openMenu(false); });
  var activeNav = $('.nav-link.active');
  if (activeNav && sidebar) {
    var top = activeNav.getBoundingClientRect().top - sidebar.getBoundingClientRect().top;
    if (top > sidebar.clientHeight - 120) sidebar.scrollTop = top - sidebar.clientHeight / 2;
  }

  /* ------------------------------------------------------------ копирование кода */
  $$('.code .copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var code = btn.parentNode.querySelector('code');
      var text = code ? code.textContent : '';
      function ok() { btn.textContent = 'Скопировано ✓'; btn.classList.add('ok'); setTimeout(function () { btn.textContent = 'Копировать'; btn.classList.remove('ok'); }, 1600); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fallback); else fallback();
      function fallback() {
        var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.top = '-1000px';
        document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); ok(); } catch (e) { /* ничего */ } document.body.removeChild(ta);
      }
    });
  });

  /* ------------------------------------------------------------ вкладки */
  $$('.tabs').forEach(function (tabs) {
    $$('.tab', tabs).forEach(function (tab) {
      tab.addEventListener('click', function () {
        var label = tab.textContent.trim();
        // синхронизируем все вкладки с той же подписью на странице
        $$('.tabs').forEach(function (other) {
          var match = $$('.tab', other).filter(function (t) { return t.textContent.trim() === label; })[0];
          if (match) activateTab(other, match.getAttribute('data-tab'));
        });
      });
    });
  });
  function activateTab(tabs, idx) {
    $$('.tab', tabs).forEach(function (t) { var on = t.getAttribute('data-tab') === idx; t.classList.toggle('active', on); t.setAttribute('aria-selected', on ? 'true' : 'false'); });
    $$('.tab-panel', tabs).forEach(function (p) { p.classList.toggle('active', p.getAttribute('data-tab') === idx); });
  }

  /* ------------------------------------------------------------ карточки самопроверки */
  $$('.quiz').forEach(function (quiz) {
    $$('.qcard-q', quiz).forEach(function (q) {
      q.addEventListener('click', function () {
        var card = q.parentNode; var on = !card.classList.contains('open');
        card.classList.toggle('open', on); q.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
    });
    var all = $('.quiz-all', quiz);
    if (all) all.addEventListener('click', function () {
      var cards = $$('.qcard', quiz);
      var open = cards.some(function (c) { return !c.classList.contains('open'); });
      cards.forEach(function (c) { c.classList.toggle('open', open); $('.qcard-q', c).setAttribute('aria-expanded', open ? 'true' : 'false'); });
      all.textContent = open ? 'Скрыть все' : 'Раскрыть все';
    });
  });

  /* ------------------------------------------------------------ оглавление: подсветка текущего */
  var tocLinks = $$('.toc-list a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var heads = $$('.doc-body h2[id], .doc-body h3[id], .all-page[id], .all-part[id]');
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) current = e.target.id; });
      if (current && map[current]) {
        tocLinks.forEach(function (a) { a.classList.remove('active'); });
        map[current].classList.add('active');
      }
    }, { rootMargin: '-64px 0px -70% 0px', threshold: 0 });
    heads.forEach(function (h) { io.observe(h); });
  }

  /* ------------------------------------------------------------ наверх */
  var toTop = $('#to-top');
  if (toTop) {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () { toTop.classList.toggle('show', window.scrollY > 700); ticking = false; });
    }, { passive: true });
    toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ------------------------------------------------------------ поиск */
  var searchEl = $('#search'), input = $('#search-input'), results = $('#search-results');
  var INDEX = window.SEARCH_INDEX || [];
  INDEX.forEach(function (e) {
    e.lp = e.p.toLowerCase(); e.lh = (e.h || '').toLowerCase(); e.lt = (e.t || '').toLowerCase(); e.lc = (e.c || '').toLowerCase();
  });
  var selected = 0, lastQuery = null;

  function openSearch() {
    if (!searchEl) return;
    searchEl.hidden = false; body.classList.add('search-open');
    input.value = ''; render(''); setTimeout(function () { input.focus(); }, 10);
  }
  function closeSearch() { if (!searchEl) return; searchEl.hidden = true; body.classList.remove('search-open'); }
  $$('#search-btn, [data-open-search]').forEach(function (b) { b.addEventListener('click', openSearch); });
  $$('[data-close]', searchEl || document).forEach(function (b) { b.addEventListener('click', closeSearch); });

  function escapeHtml(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(text, toks) {
    var out = escapeHtml(text);
    toks.forEach(function (t) {
      if (!t) return;
      var re = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
      out = out.replace(re, '<mark>$1</mark>');
    });
    return out;
  }
  function snippet(text, toks) {
    var low = text.toLowerCase(), pos = -1;
    for (var i = 0; i < toks.length; i++) { pos = low.indexOf(toks[i]); if (pos >= 0) break; }
    if (pos < 0) return text.slice(0, 140) + (text.length > 140 ? '…' : '');
    var start = Math.max(0, pos - 60), end = Math.min(text.length, pos + 100);
    return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
  }
  function search(q) {
    var toks = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!toks.length) return [];
    var out = [];
    for (var i = 0; i < INDEX.length; i++) {
      var e = INDEX[i], score = 0, okAll = true;
      for (var k = 0; k < toks.length; k++) {
        var t = toks[k], s = 0;
        if (e.lp.indexOf(t) >= 0) s += 8;
        if (e.lh.indexOf(t) >= 0) s += 10;
        if (e.lc.indexOf(t) >= 0) s += 5;
        if (e.lt.indexOf(t) >= 0) s += 2;
        if (!s) { okAll = false; break; }
        score += s;
      }
      if (!okAll) continue;
      if (e.lh === toks.join(' ')) score += 20;
      if (!e.a) score += 1;
      out.push({ e: e, s: score });
    }
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 40);
  }
  function render(q) {
    if (!results) return;
    var toks = q.toLowerCase().split(/\s+/).filter(Boolean);
    var html = '';
    if (!toks.length) {
      html += '<div class="sr-group">Разделы</div>';
      PAGES.forEach(function (p) {
        html += '<a class="sr-item" href="' + p.id + '.html"><span class="sr-title">' + escapeHtml(p.t) + '</span></a>';
      });
    } else {
      var found = search(q);
      if (!found.length) {
        html = '<div class="sr-empty">Ничего не нашлось. Попробуйте другое слово — например, имя класса или метода.</div>';
      } else {
        var lastPage = null;
        found.forEach(function (r) {
          var e = r.e;
          if (e.p !== lastPage) { html += '<div class="sr-group">' + escapeHtml(e.g) + ' · ' + escapeHtml(e.p) + '</div>'; lastPage = e.p; }
          var url = e.u + (e.a ? '#' + e.a : '');
          var text = e.t || e.c || '';
          html += '<a class="sr-item" href="' + url + '">' +
            '<span class="sr-title">' + mark(e.h || e.p, toks) + '</span>' +
            (text ? '<span class="sr-text">' + mark(snippet(text, toks), toks) + '</span>' : '') + '</a>';
        });
      }
    }
    results.innerHTML = html;
    selected = 0; highlight();
  }
  function items() { return $$('.sr-item', results); }
  function highlight() {
    var list = items();
    list.forEach(function (el, i) { el.classList.toggle('selected', i === selected); });
    if (list[selected]) list[selected].scrollIntoView({ block: 'nearest' });
  }
  if (input) {
    input.addEventListener('input', function () { if (input.value !== lastQuery) { lastQuery = input.value; render(input.value); } });
    input.addEventListener('keydown', function (e) {
      var list = items();
      if (e.key === 'ArrowDown') { e.preventDefault(); selected = Math.min(list.length - 1, selected + 1); highlight(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); selected = Math.max(0, selected - 1); highlight(); }
      else if (e.key === 'Enter') { e.preventDefault(); if (list[selected]) window.location.href = list[selected].getAttribute('href'); }
    });
    results.addEventListener('mousemove', function (e) {
      var a = e.target.closest('.sr-item'); if (!a) return;
      var idx = items().indexOf(a); if (idx !== selected) { selected = idx; highlight(); }
    });
  }

  /* ------------------------------------------------------------ клавиатура */
  document.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase();
    var typing = tag === 'input' || tag === 'textarea' || e.target.isContentEditable;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if (searchEl && searchEl.hidden) openSearch(); else closeSearch(); return; }
    if (e.key === 'Escape') { if (searchEl && !searchEl.hidden) closeSearch(); else openMenu(false); return; }
    if (typing) return;
    if (e.key === '/') { e.preventDefault(); openSearch(); return; }
    if (e.key === '[' || e.key === ']') {
      var link = $(e.key === '[' ? '.pager-link.prev' : '.pager-link.next');
      if (link) window.location.href = link.getAttribute('href');
    }
  });

  /* ------------------------------------------------------------ якоря при загрузке с #hash под фиксированной шапкой */
  if (location.hash) {
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) setTimeout(function () { target.scrollIntoView(); window.scrollBy(0, -72); }, 0);
  }
})();
