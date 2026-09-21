/* Справочник PHP 8+ — навигация по каталогу и живые демонстрации. */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватный режим */ } }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  /* ключи общие с курсом и хабом: тема должна переноситься между страницами */
  /* тема общая со всем сайтом, поэтому ключ тот же, что у остальных страниц */
  var KEY_THEME = 'yii2:theme';
  var KEY_DONE = 'php:explorer-done';
  var KEY_QUICK = 'php:explorer-quick';

  /* --------------------------------------------------------------------------- тема */

  var themeBtn = $('#theme-btn');

  function applyTheme(mode) {
    if (mode === 'dark' || mode === 'light') root.setAttribute('data-theme', mode);
    else root.removeAttribute('data-theme');
  }
  applyTheme(read(KEY_THEME));

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = root.getAttribute('data-theme');
      var dark = current === 'dark' || (!current && window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);
      var next = dark ? 'light' : 'dark';
      applyTheme(next);
      store(KEY_THEME, next);
    });
  }

  /* ------------------------------------------------------------- изученные узлы */

  var learnCheck = $('#learn-check');
  var learnedBox = $('#learned');
  var learnedNum = $('#learned-n');

  function doneList() {
    try { var a = JSON.parse(read(KEY_DONE) || '[]'); return Array.isArray(a) ? a : []; }
    catch (e) { return []; }
  }

  function renderDone() {
    var done = doneList();
    $$('[data-open]').forEach(function (el) {
      el.classList.toggle('is-done', done.indexOf(el.getAttribute('data-open')) >= 0);
    });
    if (learnedNum) learnedNum.textContent = done.length;
    if (learnedBox) learnedBox.hidden = done.length === 0;
    if (learnCheck && current) learnCheck.checked = done.indexOf(current) >= 0;
  }

  function setDone(id, on) {
    var a = doneList().filter(function (x) { return x !== id; });
    if (on) a.push(id);
    store(KEY_DONE, JSON.stringify(a));
    renderDone();
  }

  if (learnCheck) learnCheck.addEventListener('change', function () {
    if (current) setDone(current, learnCheck.checked);
  });

  var learnedReset = $('#learned-reset');
  if (learnedReset) learnedReset.addEventListener('click', function () {
    if (confirm('Сбросить отметки об изученных узлах?')) { store(KEY_DONE, '[]'); renderDone(); }
  });

  /* ------------------------------------------------------- быстрый режим */

  var quickBtn = $('#quick-btn');
  var quickTab = quickBtn ? quickBtn.getAttribute('data-tab') : null;
  var quick = read(KEY_QUICK) === '1';

  function renderQuick() {
    if (quickBtn) quickBtn.setAttribute('aria-pressed', quick ? 'true' : 'false');
  }
  renderQuick();

  if (quickBtn) quickBtn.addEventListener('click', function () {
    quick = !quick;
    store(KEY_QUICK, quick ? '1' : '0');
    renderQuick();
  });

  /* --------------------------------------------------------------------------- панель */

  var panel = $('#panel');
  var scrim = $('#scrim');
  var panelBody = $('#panel-body-in');
  var panelTitle = $('#pb-title');
  var store_ = $('#topic-store');
  var current = null;
  var lastFocused = null;

  function openTopic(id, tabId, push) {
    var node = document.getElementById('topic-' + id);
    if (!node) return;
    if (current === id) { if (tabId) selectTab(node, tabId); return; }

    closeTopic(false);
    lastFocused = document.activeElement;
    current = id;
    if (learnCheck) learnCheck.checked = doneList().indexOf(id) >= 0;

    panelBody.appendChild(node);
    node.hidden = false;
    panel.style.setProperty('--pc', node.getAttribute('data-color') || '');
    panelTitle.textContent = node.getAttribute('data-title');

    body.classList.add('panel-open');
    panel.hidden = false;
    scrim.hidden = false;
    if (tabId) selectTab(node, tabId);
    panelBody.parentNode.scrollTop = 0;

    if (push !== false) {
      var hash = '#' + id + (tabId ? '/' + tabId : '');
      if (location.hash !== hash) history.pushState({ topic: id }, '', hash);
    }
    var close = $('#panel-close');
    if (close) close.focus();
  }

  function closeTopic(push) {
    if (!current) return;
    var node = document.getElementById('topic-' + current);
    if (node) { node.hidden = true; store_.appendChild(node); }
    current = null;
    body.classList.remove('panel-open');
    panel.hidden = true;
    scrim.hidden = true;
    if (push !== false && location.hash) history.pushState(null, '', location.pathname + location.search);
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  function selectTab(node, tabId) {
    $$('.tab', node).forEach(function (t) {
      var on = t.getAttribute('data-tab') === tabId;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    $$('.tab-panel', node).forEach(function (p) {
      p.hidden = p.getAttribute('data-tab') !== tabId;
    });
  }

  $$('[data-open]').forEach(function (el) {
    function open(e) {
      e.preventDefault();
      openTopic(el.getAttribute('data-open'), quick ? quickTab : undefined);
    }
    el.addEventListener('click', open);
    /* узлы карты — <g role="link">: браузер не превращает Enter в клик сам */
    if (el.tagName !== 'BUTTON' && el.tagName !== 'A') {
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') open(e);
      });
    }
  });
  renderDone();

  $$('.tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      var node = tab.closest('.topic');
      var id = tab.getAttribute('data-tab');
      selectTab(node, id);
      if (current) history.replaceState({ topic: current }, '', '#' + current + '/' + id);
    });
  });

  if (scrim) scrim.addEventListener('click', function () { closeTopic(); });
  var closeBtn = $('#panel-close');
  if (closeBtn) closeBtn.addEventListener('click', function () { closeTopic(); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && current) { e.preventDefault(); closeTopic(); }
  });

  function fromHash(push) {
    var raw = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    if (!raw) { closeTopic(false); return; }
    var parts = raw.split('/');
    openTopic(parts[0], parts[1], push);
  }
  window.addEventListener('popstate', function () { fromHash(false); });

  /* --------------------------------------------------------------------------- подсказка на карте */

  var tip = $('#tip');
  var tipFor = null;

  function showTip(el) {
    if (!tip || tipFor === el) return;
    var title = el.getAttribute('data-tip-title');
    if (!title) return;
    tipFor = el;
    tip.innerHTML = '';

    var b = document.createElement('b');
    b.textContent = title;
    tip.appendChild(b);

    var cls = document.createElement('span');
    cls.className = 'tip-cls';
    cls.textContent = el.getAttribute('data-tip-cls') || '';
    tip.appendChild(cls);

    var lead = document.createElement('p');
    lead.textContent = el.getAttribute('data-tip-lead') || '';
    tip.appendChild(lead);

    var badge = el.getAttribute('data-tip-badge');
    if (badge) {
      var chip = document.createElement('span');
      chip.className = 'tip-badge';
      chip.textContent = badge;
      tip.appendChild(chip);
    }

    tip.style.setProperty('--tc', getComputedStyle(el).getPropertyValue('--gc') || '');
    tip.hidden = false;

    // сначала показываем за кадром, чтобы измерить, потом ставим на место
    var box = el.getBoundingClientRect();
    var size = tip.getBoundingClientRect();
    var left = box.left + box.width / 2 - size.width / 2;
    left = Math.max(12, Math.min(left, window.innerWidth - size.width - 12));
    var top = box.bottom + 10;
    if (top + size.height > window.innerHeight - 12) top = box.top - size.height - 10;
    tip.style.left = Math.round(left) + 'px';
    tip.style.top = Math.round(Math.max(12, top)) + 'px';
    tip.classList.add('show');
  }

  function hideTip() {
    if (!tip || tipFor === null) return;
    tipFor = null;
    tip.classList.remove('show');
    tip.hidden = true;
  }

  if (tip && matchMedia('(hover: hover)').matches) {
    $$('.mp-hit').forEach(function (el) {
      el.addEventListener('mouseenter', function () { showTip(el); });
      el.addEventListener('mouseleave', hideTip);
    });
  }
  if (tip) {
    $$('.mp-hit').forEach(function (el) {
      el.addEventListener('focus', function () { showTip(el); });
      el.addEventListener('blur', hideTip);
    });
    window.addEventListener('scroll', hideTip, { passive: true });
    window.addEventListener('resize', hideTip);
  }

  /* --------------------------------------------------------------------------- копирование кода */

  $$('.copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.closest('.code').querySelector('pre');
      var text = pre ? pre.textContent : '';
      function done() {
        btn.textContent = 'скопировано';
        btn.classList.add('done');
        setTimeout(function () { btn.textContent = 'копировать'; btn.classList.remove('done'); }, 1500);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else { fallback(); }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.top = '-1000px';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); } catch (err) { /* нечего делать */ }
        document.body.removeChild(ta);
      }
    });
  });

  /* --------------------------------------------------------------------------- справочники: фильтр */

  /* держать в паре с .ref-work в explorer.css */
  var STACK_Q = '(max-width: 900px)';

  $$('.ref-block').forEach(function (block) {
    var input = $('.ref-search input', block);
    var count = $('.ref-count', block);
    var work = $('.ref-work', block);
    var pane = $('.ref-pane', block);
    var items = $$('.ref-item', block);
    var empty = $('.ref-empty', block);
    var total = items.length;
    if (!work || !pane || !total) return;

    var rpName = $('.rp-name', pane);
    var rpDesc = $('.rp-desc', pane);
    var rpBody = $('.rp-body', pane);
    var narrow = window.matchMedia(STACK_Q);
    var hoverable = window.matchMedia('(hover: hover)').matches;
    var active = items[0];

    /* на узком экране панель стоит под выбранным пунктом, на широком — в правой колонке */
    function place() {
      if (narrow.matches) active.parentNode.insertBefore(pane, active.nextSibling);
      else work.appendChild(pane);
    }

    function show(item) {
      if (!item) return;
      if (item === active) { place(); return; }
      $('.ref-btn', active).removeAttribute('aria-current');
      active.classList.remove('is-active');
      active = item;
      active.classList.add('is-active');
      var btn = $('.ref-btn', active);
      btn.setAttribute('aria-current', 'true');
      rpName.textContent = $('.ref-n', btn).textContent;
      rpDesc.innerHTML = $('.ref-d', btn).innerHTML;
      rpBody.innerHTML = $('.ref-body', active).innerHTML;
      place();
      markOverflow();
    }

    /* длинная строка прокручивается — отмечаем это тенью, иначе читается как обрезка */
    function markOverflow() {
      var fig = $('.code', rpBody);
      var pre = fig && $('pre', fig);
      if (!pre) return;
      var more = function () {
        fig.classList.toggle('has-more', pre.scrollWidth - pre.scrollLeft - pre.clientWidth > 2);
      };
      more();
      pre.addEventListener('scroll', more, { passive: true });
    }

    function visible() {
      return items.filter(function (it) { return !it.hidden; });
    }

    /* стрелками — к соседнему пункту; фокус сам покажет его в панели */
    function step(dir) {
      var vis = visible();
      var next = vis[vis.indexOf(active) + dir];
      if (next) $('.ref-btn', next).focus();
    }

    items.forEach(function (item) {
      var btn = $('.ref-btn', item);
      btn.addEventListener('click', function () { show(item); });
      btn.addEventListener('focus', function () { show(item); });
      if (hoverable) btn.addEventListener('mouseenter', function () { show(item); });
      btn.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); step(1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); step(-1); }
      });
    });

    place();
    markOverflow();
    if (narrow.addEventListener) narrow.addEventListener('change', place);

    if (!input) return;
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      items.forEach(function (item) {
        var hit = !q || item.getAttribute('data-search').indexOf(q) >= 0;
        item.hidden = !hit;
        if (hit) shown++;
      });
      count.textContent = q ? shown + ' из ' + total : total + ' шт.';
      if (empty) empty.hidden = shown > 0;
      work.hidden = shown === 0;
      /* выбранный пункт мог уйти под фильтр — показываем первый оставшийся */
      if (shown && active.hidden) show(visible()[0]);
    });
  });

  /* --------------------------------------------------------------------------- демо */

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* --------------------------------------------------------------------------- данные */

  /* таблицы посчитал сам PHP при сборке страницы: src/php/data/gen.php */
  var DATA = window.PHPREF || { compare: null, types: null, versions: [] };

  function chip(label, pressed) {
    return '<button type="button" class="chip" data-v="' + esc(label) + '" aria-pressed="' +
      (pressed ? 'true' : 'false') + '">' + esc(label) + '</button>';
  }

  function pickChip(box, value) {
    $$('.chip', box).forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === value));
    });
  }

  function kvRows(pairs) {
    return pairs.map(function (p) {
      return '<div class="kv-row"><div class="kv-k">' + esc(p[0]) +
        '</div><div class="kv-v">' + p[1] + '</div></div>';
    }).join('');
  }

  /* --------------------------------------------------------- демо 1: сравнение значений */

  function initCompareLab(root) {
    var data = DATA.compare;
    if (!data) return;

    var labels = data.values.map(function (v) { return String(v.label); });
    var boxA = $('[data-role="a"]', root);
    var boxB = $('[data-role="b"]', root);
    var verdict = $('[data-role="verdict"]', root);
    var table = $('[data-role="table"]', root);
    var note = $('[data-role="note"]', root);
    var a = "'abc'";
    var b = '0';

    boxA.innerHTML = labels.map(function (l) { return chip(l, l === a); }).join('');
    boxB.innerHTML = labels.map(function (l) { return chip(l, l === b); }).join('');

    function cell(v, key) { return '<code>' + esc(v[key]) + '</code>'; }

    function render() {
      var i = labels.indexOf(a);
      var j = labels.indexOf(b);
      var va = data.values[i];
      var vb = data.values[j];
      var eq = data.eq[i][j] === 1;
      var id = data.id[i][j] === 1;
      var cmp = data.cmp[i][j];

      verdict.className = 'verdict ' + (eq ? 'pass' : 'fail');
      verdict.innerHTML = '<b><code>' + esc(a) + ' == ' + esc(b) + '</code> → ' +
        (eq ? 'true' : 'false') + '</b><span class="vtext">' +
        '<code>===</code> → ' + (id ? 'true' : 'false') +
        ' · <code>&lt;=&gt;</code> → ' + cmp + '</span>';

      table.innerHTML =
        '<tr><th></th><th>' + esc(a) + '</th><th>' + esc(b) + '</th></tr>' +
        '<tr><td>тип</td><td>' + cell(va, 'type') + '</td><td>' + cell(vb, 'type') + '</td></tr>' +
        '<tr><td>(bool)</td><td>' + cell(va, 'bool') + '</td><td>' + cell(vb, 'bool') + '</td></tr>' +
        '<tr><td>(int)</td><td>' + cell(va, 'int') + '</td><td>' + cell(vb, 'int') + '</td></tr>' +
        '<tr><td>(float)</td><td>' + cell(va, 'float') + '</td><td>' + cell(vb, 'float') + '</td></tr>' +
        '<tr><td>(string)</td><td>' + cell(va, 'string') + '</td><td>' + cell(vb, 'string') + '</td></tr>' +
        '<tr><td>empty()</td><td>' + (va.empty ? 'true' : 'false') +
        '</td><td>' + (vb.empty ? 'true' : 'false') + '</td></tr>';

      var hints = [];
      if (eq && !id) hints.push('равны нестрого, но не строго: типы разные');
      if (!eq && va.type === vb.type) hints.push('одинаковый тип и всё равно не равны — сравниваются значения');
      if (va.numeric === false || vb.numeric === false) {
        hints.push('нечисловая строка в PHP 8 сравнивается с числом как строка, а не как ноль');
      }
      if (cmp === 0 && !id) hints.push('<code>&lt;=&gt;</code> считает их равными: сортировка не сохранит порядок');
      note.innerHTML = hints.length ? hints.join('. ') + '.' : '';
    }

    boxA.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      a = btn.getAttribute('data-v');
      pickChip(boxA, a);
      render();
    });
    boxB.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      b = btn.getAttribute('data-v');
      pickChip(boxB, b);
      render();
    });
    render();
  }

  /* ------------------------------------------------- демо 2: что сделает объявленный тип */

  function initTypesLab(root) {
    var data = DATA.types;
    if (!data) return;

    var typeSel = $('#tl-type', root);
    var valueSel = $('#tl-value', root);
    var call = $('[data-role="call"]', root);
    var weakBox = $('[data-role="weak"]', root);
    var strictBox = $('[data-role="strict"]', root);
    var note = $('[data-role="note"]', root);

    typeSel.innerHTML = data.types.map(function (t) {
      return '<option value="' + esc(t) + '"' + (t === 'int' ? ' selected' : '') + '>' + esc(t) + '</option>';
    }).join('');
    valueSel.innerHTML = data.values.map(function (v) {
      return '<option value="' + esc(v) + '"' + (v === "'42'" ? ' selected' : '') + '>' + esc(v) + '</option>';
    }).join('');

    function verdict(box, title, cell) {
      var ok = cell.ok;
      box.className = 'verdict ' + (ok ? (cell.kept ? 'pass' : '') : 'fail');
      var what = ok
        ? (cell.kept ? 'принято как есть' : 'приведено к <code>' + esc(cell.got) + '</code>')
        : 'TypeError';
      box.innerHTML = '<b>' + esc(title) + '</b><span class="vtext">' + what + '</span>';
    }

    function render() {
      var t = typeSel.value;
      var v = valueSel.value;
      var weak = data.weak[t][v];
      var strict = data.strict[t][v];

      call.textContent = 'function probe(' + t + ' $x) { return $x; }\n\nprobe(' + v + ');';
      verdict(weakBox, 'обычный режим', weak);
      verdict(strictBox, 'declare(strict_types=1)', strict);

      var lines = [];
      if (weak.note) lines.push(weak.note);
      if (strict.note && strict.note !== weak.note) lines.push('строгий режим: ' + strict.note);
      if (!lines.length && weak.ok && strict.ok && weak.kept && strict.kept) {
        lines.push('значение подходит объявленному типу — режим ни на что не влияет');
      }
      note.textContent = lines.join(' · ');
    }

    typeSel.addEventListener('change', render);
    valueSel.addEventListener('change', render);
    render();
  }

  /* ------------------------------------------------------- демо 3: строка — это байты */

  function initBytesLab(root) {
    var input = $('#bl-input', root);
    var samples = $('[data-role="samples"]', root);
    var table = $('[data-role="table"]', root);
    var split = $('[data-role="split"]', root);
    var note = $('[data-role="note"]', root);
    var encoder = window.TextEncoder ? new TextEncoder() : null;
    var seg = window.Intl && Intl.Segmenter ? new Intl.Segmenter('ru', { granularity: 'grapheme' }) : null;

    var SAMPLES = ['Привет, PHP!', 'naïve café', '👨‍👩‍👦 семья', 'ASCII only'];
    samples.innerHTML = SAMPLES.map(function (s) { return chip(s, false); }).join('');

    function bytes(s) { return encoder ? encoder.encode(s).length : s.length; }
    function chars(s) { return Array.from(s).length; }
    function graphemes(s) {
      if (!seg) return chars(s);
      var n = 0;
      var it = seg.segment(s)[Symbol.iterator]();
      var step = it.next();
      while (!step.done) { n++; step = it.next(); }
      return n;
    }

    function render() {
      var s = input.value;
      var byteLen = bytes(s);
      var charLen = chars(s);
      var graphLen = graphemes(s);

      table.innerHTML = kvRows([
        ['strlen($s)', '<code>' + byteLen + '</code> — байтов'],
        ['mb_strlen($s)', '<code>' + charLen + '</code> — символов'],
        ['«на глаз»', '<code>' + graphLen + '</code> — видимых знаков'],
        ['substr($s, 0, 4)', '<code>' + esc(JSON.stringify(sliceBytes(s, 4))) + '</code> — по байтам'],
        ['mb_substr($s, 0, 4)', '<code>' + esc(JSON.stringify(Array.from(s).slice(0, 4).join(''))) + '</code> — по символам'],
        ['strtoupper($s)', '<code>' + esc(s.replace(/[a-z]/g, function (c) { return c.toUpperCase(); })) + '</code> — только латиница'],
        ['mb_strtoupper($s)', '<code>' + esc(s.toUpperCase()) + '</code>'],
      ]);

      split.innerHTML = Array.from(s).slice(0, 24).map(function (ch) {
        var n = bytes(ch);
        return '<b data-n="' + n + '">' + esc(ch === ' ' ? '␣' : ch) + '<i>' + n + '</i></b>';
      }).join('') + (charLen > 24 ? '<span class="bytes-more">…</span>' : '');

      note.textContent = byteLen === charLen
        ? 'Пока в строке только ASCII, байт и символ — одно и то же, и разницы не видно.'
        : 'В строке ' + byteLen + ' байт на ' + charLen + ' символов' +
          (graphLen !== charLen ? ', а видимых знаков и вовсе ' + graphLen : '') +
          ': байтовые функции будут резать символы пополам.';
    }

    /* substr() режет по байтам: показываем, что получится, вплоть до битого хвоста */
    function sliceBytes(s, n) {
      if (!encoder || !window.TextDecoder) return s.slice(0, n);
      var cut = encoder.encode(s).slice(0, n);
      return new TextDecoder('utf-8').decode(cut);
    }

    input.addEventListener('input', render);
    samples.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      input.value = btn.getAttribute('data-v');
      pickChip(samples, input.value);
      render();
    });
    render();
  }

  /* ------------------------------------------------------- демо 4: что даёт версия */

  function initVersionLab(root) {
    var versions = DATA.versions || [];
    if (!versions.length) return;

    var box = $('[data-role="vers"]', root);
    var head = $('[data-role="head"]', root);
    var added = $('[data-role="added"]', root);
    var note = $('[data-role="note"]', root);
    var current = versions[versions.length - 1].v;

    box.innerHTML = versions.map(function (v) { return chip(v.v, v.v === current); }).join('');

    function render() {
      var v = versions.filter(function (x) { return x.v === current; })[0];
      var supported = v.state.indexOf('не поддерживается') === -1;

      head.className = 'verdict ' + (supported ? 'pass' : 'fail');
      head.innerHTML = '<b>PHP ' + esc(v.v) + ' · ' + esc(v.date) + '</b>' +
        '<span class="vtext">' + esc(v.state) + '. ' + esc(v.lead) + '</span>';

      added.innerHTML = kvRows(v.added.map(function (pair) {
        return [pair[0], esc(pair[1])];
      }));

      note.innerHTML = '<b>перестало работать или устарело:</b> ' +
        v.gone.map(function (pair) {
          return esc(pair[0]) + ' — ' + esc(pair[1]);
        }).join('; ') + '.';
    }

    box.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      current = btn.getAttribute('data-v');
      pickChip(box, current);
      render();
    });
    render();
  }

  /* --------------------------------------------------------------------------- запуск всех демо */

  var DEMOS = {
    'compare-lab': initCompareLab,
    'types-lab': initTypesLab,
    'bytes-lab': initBytesLab,
    'version-lab': initVersionLab
  };

  $$('[data-demo]').forEach(function (el) {
    var fn = DEMOS[el.getAttribute('data-demo')];
    if (!fn) return;
    try { fn(el); } catch (e) { if (window.console) console.error('демо не запустилось:', el.getAttribute('data-demo'), e); }
  });

  /* стартовое состояние из адреса */
  fromHash(false);
})();
