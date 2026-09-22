/* Проверка знаний Yii 2 — сборка набора, прохождение, разбор ошибок.
   Вопросы приходят готовой разметкой в window.QUIZ: подсветка кода и
   инлайновый `код` сделаны на сборке, здесь только перемешивание и логика. */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var KEY_THEME = 'yii2:theme';
  var KEY_STATE = 'yii2:quiz';

  var DATA = window.QUIZ || { topics: [], questions: [] };
  var BY_ID = {};
  DATA.questions.forEach(function (q) { BY_ID[q.id] = q; });
  var TOPIC = {};
  DATA.topics.forEach(function (t) { TOPIC[t.id] = t; });
  var CHAPTER = DATA.chapters || {};

  var QUICK = 10, EXAM = 40;

  /* ------------------------------------------------------------ хранилище */

  function load() {
    try {
      var raw = localStorage.getItem(KEY_STATE);
      var o = raw ? JSON.parse(raw) : null;
      if (o && o.stats) { return o; }
    } catch (e) {}
    return { stats: {} };
  }

  function save(o) {
    try { localStorage.setItem(KEY_STATE, JSON.stringify(o)); } catch (e) {}
  }

  var store = load();

  function record(id, right) {
    var s = store.stats[id] || (store.stats[id] = { n: 0, w: 0, last: 0 });
    s.n++;
    if (!right) { s.w++; }
    s.last = right ? 0 : 1;           // 1 — в прошлый раз ошибся, попадёт в работу над ошибками
    save(store);
  }

  function missedIds() {
    return Object.keys(store.stats).filter(function (id) {
      return store.stats[id].last === 1 && BY_ID[id];
    });
  }

  /* -------------------------------------------------------------- утилиты */

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function plural(n, one, few, many) {
    var m = Math.abs(n) % 100;
    if (m >= 11 && m <= 19) { return many; }
    m %= 10;
    if (m === 1) { return one; }
    if (m >= 2 && m <= 4) { return few; }
    return many;
  }

  function same(a, b) {
    if (a.length !== b.length) { return false; }
    var x = a.slice().sort(), y = b.slice().sort();
    return x.every(function (v, i) { return v === y[i]; });
  }

  /* ---------------------------------------------------------- набор вопросов */

  var run = null;      // { items: [...], pos, done: [] }

  function prepare(list) {
    return list.map(function (q) {
      var order = shuffle(q.options.map(function (_, i) { return i; }));
      return {
        q: q,
        order: order,                                   // порядок показа вариантов
        answer: order.reduce(function (acc, src, shown) {
          if (q.answer.indexOf(src) >= 0) { acc.push(shown); }
          return acc;
        }, []),
        picked: [],
        checked: false,
        right: false
      };
    });
  }

  function start(mode, arg) {
    var pool = DATA.questions.slice();
    var title = '';
    if (mode === 'quick') {
      pool = shuffle(pool).slice(0, QUICK);
      title = 'Быстрый прогон';
    } else if (mode === 'exam') {
      pool = shuffle(pool).slice(0, EXAM);
      title = 'Экзамен';
    } else if (mode === 'topic') {
      pool = shuffle(pool.filter(function (q) { return q.topic === arg; }));
      title = TOPIC[arg] ? TOPIC[arg].title : 'Тема';
    } else if (mode === 'chapter') {
      pool = shuffle(pool.filter(function (q) { return q.page === arg; }));
      title = 'Раздел: ' + (CHAPTER[arg] || arg);
    } else if (mode === 'missed') {
      var ids = missedIds();
      pool = shuffle(pool.filter(function (q) { return ids.indexOf(q.id) >= 0; }));
      title = 'Работа над ошибками';
    }
    if (!pool.length) { return; }
    run = { items: prepare(pool), pos: 0, title: title, mode: mode, arg: arg };
    show('run');
    render();
  }

  /* ------------------------------------------------------------- отрисовка */

  /* Единственная прокрутка, которую делает страница: вернуть взгляд к началу
     нового вопроса, и только если читатель сам уехал вниз. Подтягивать разбор
     не нужно — он выводится сразу под кнопкой, по которой только что кликнули,
     а на невысоком окне такая доводка читается как рывок. */
  function topOfRun() {
    var el = $('#screen-run');
    return el.getBoundingClientRect().top + window.pageYOffset - 64;
  }

  function anchorQuestion() {
    var top = Math.max(0, topOfRun());
    if (window.pageYOffset > top + 1) { window.scrollTo(0, top); }
  }

  function show(what) {
    $('#screen-start').hidden = what !== 'start';
    $('#screen-run').hidden = what !== 'run';
    $('#screen-result').hidden = what !== 'result';
    window.scrollTo(0, 0);
  }

  function render() {
    var it = run.items[run.pos];
    var q = it.q;
    var t = TOPIC[q.topic] || { title: '', color: 'var(--signal)' };

    $('#rb-title').textContent = run.title;
    $('#rb-pos').textContent = (run.pos + 1) + ' / ' + run.items.length;

    var dots = run.items.map(function (x, i) {
      var cls = 'qp';
      if (x.checked) { cls += x.right ? ' is-ok' : ' is-no'; }
      if (i === run.pos) { cls += ' is-now'; }
      return '<span class="' + cls + '"></span>';
    }).join('');
    $('#qprog').innerHTML = dots;

    var box = $('#qbox');
    box.style.setProperty('--tc', t.color);
    $('#q-topic').textContent = t.title;
    $('#q-kind').textContent = q.kind === 'many' ? 'несколько верных' : 'один верный';
    $('#q-text').innerHTML = q.text;

    var code = $('#q-code');
    if (q.code) { code.innerHTML = q.code; code.hidden = false; } else { code.hidden = true; }

    $('#opts').innerHTML = it.order.map(function (src, shown) {
      var cls = 'opt' + (q.kind === 'many' ? ' many' : '') + (q.mono ? ' mono' : '');
      return '<button type="button" class="' + cls + '" data-i="' + shown + '" aria-pressed="false">' +
             '<span class="opt-k">' + (shown + 1) + '</span>' +
             '<span class="opt-t">' + q.options[src] + '</span></button>';
    }).join('');

    $('#verdict').hidden = true;
    var btn = $('#act-main');
    btn.textContent = 'Проверить';
    btn.disabled = true;
    $('#act-skip').hidden = false;
    bindOptions();
    anchorQuestion();
  }

  function bindOptions() {
    $$('.opt', $('#opts')).forEach(function (el) {
      el.addEventListener('click', function () { pick(+el.getAttribute('data-i')); });
    });
  }

  function pick(i) {
    var it = run.items[run.pos];
    if (it.checked) { return; }
    if (it.q.kind === 'many') {
      var at = it.picked.indexOf(i);
      if (at >= 0) { it.picked.splice(at, 1); } else { it.picked.push(i); }
    } else {
      it.picked = [i];
    }
    $$('.opt', $('#opts')).forEach(function (el) {
      var on = it.picked.indexOf(+el.getAttribute('data-i')) >= 0;
      el.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    $('#act-main').disabled = !it.picked.length;
  }

  function check() {
    var it = run.items[run.pos];
    var q = it.q;
    it.checked = true;
    it.right = same(it.picked, it.answer);
    record(q.id, it.right);

    $$('.opt', $('#opts')).forEach(function (el) {
      var i = +el.getAttribute('data-i');
      el.disabled = true;
      if (it.answer.indexOf(i) >= 0) { el.classList.add('is-right'); }
      else if (it.picked.indexOf(i) >= 0) { el.classList.add('is-wrong'); }
    });

    var v = $('#verdict');
    v.className = 'verdict ' + (it.right ? 'ok' : 'no');
    $('#v-head').textContent = it.right ? 'Верно' : 'Мимо';
    $('#v-why').innerHTML = q.why;
    $('#v-links').innerHTML = (q.links || []).map(function (l) {
      return '<a href="' + l.href + '">' + l.label + '</a>';
    }).join('');
    v.hidden = false;

    var btn = $('#act-main');
    btn.disabled = false;
    btn.textContent = run.pos + 1 < run.items.length ? 'Дальше' : 'Итог';
    $('#act-skip').hidden = true;
    render_dots();
  }

  function render_dots() {
    $('#qprog').innerHTML = run.items.map(function (x, i) {
      var cls = 'qp';
      if (x.checked) { cls += x.right ? ' is-ok' : ' is-no'; }
      if (i === run.pos) { cls += ' is-now'; }
      return '<span class="' + cls + '"></span>';
    }).join('');
  }

  function next() {
    if (run.pos + 1 < run.items.length) { run.pos++; render(); }
    else { finish(); }
  }

  function skip() {
    var it = run.items[run.pos];
    it.checked = true;
    it.right = false;
    record(it.q.id, false);
    next();
  }

  /* ----------------------------------------------------------------- итог */

  function finish() {
    var total = run.items.length;
    var right = run.items.filter(function (x) { return x.right; }).length;
    var pct = Math.round(right / total * 100);

    var el = $('#score-n');
    el.textContent = right + ' / ' + total;
    var color = pct >= 80 ? 'var(--ok)' : (pct >= 50 ? 'var(--warn)' : 'var(--bad)');
    el.style.setProperty('--sc', color);

    $('#score-h').textContent = pct >= 80 ? 'Уверенно' : (pct >= 50 ? 'Есть провалы' : 'Стоит перечитать');
    $('#score-p').textContent = pct + '% верных ответов · ' + run.title.toLowerCase();

    var byTopic = {};
    run.items.forEach(function (x) {
      var b = byTopic[x.q.topic] || (byTopic[x.q.topic] = { n: 0, ok: 0 });
      b.n++;
      if (x.right) { b.ok++; }
    });
    $('#by-topic').innerHTML = Object.keys(byTopic).map(function (id) {
      var b = byTopic[id], t = TOPIC[id] || { title: id };
      var p = Math.round(b.ok / b.n * 100);
      return '<div class="bt-row"><span class="bt-n">' + t.title + '</span>' +
             '<span class="bt-bar"><i style="width:' + p + '%"></i></span>' +
             '<span class="bt-c">' + b.ok + '/' + b.n + '</span></div>';
    }).join('');

    var missed = run.items.filter(function (x) { return !x.right; });
    $('#misses-h').hidden = !missed.length;
    $('#misses').innerHTML = missed.map(function (x) {
      var right = x.answer.map(function (shown) { return x.q.options[x.order[shown]]; }).join(' · ');
      return '<div class="miss"><p class="m-q">' + x.q.text + '</p>' +
             '<p class="m-a">Верно: <b>' + right + '</b></p></div>';
    }).join('');

    $('#again-missed').hidden = !missed.length;
    show('result');
  }

  /* --------------------------------------------------------------- экран старта */

  function paintStart() {
    var ids = missedIds();
    var btn = $('#mode-missed');
    btn.disabled = !ids.length;
    $('#missed-note').textContent = ids.length
      ? ids.length + ' ' + plural(ids.length, 'вопрос', 'вопроса', 'вопросов') + ', где вы ошиблись в прошлый раз'
      : 'Пока пусто — сначала пройдите любой набор';

    var seen = Object.keys(store.stats).filter(function (id) { return BY_ID[id]; });
    $('#seen-note').textContent = seen.length
      ? 'Отвечено на ' + seen.length + ' из ' + DATA.questions.length
      : 'Ещё ни одного ответа';

    $('#topics').innerHTML = DATA.topics.map(function (t) {
      var list = DATA.questions.filter(function (q) { return q.topic === t.id; });
      var ok = list.filter(function (q) {
        var s = store.stats[q.id];
        return s && s.last === 0;
      }).length;
      var p = list.length ? Math.round(ok / list.length * 100) : 0;
      return '<button type="button" class="topic" data-topic="' + t.id + '" style="--tc: ' + t.color + '">' +
             '<span class="t-n">' + t.title + '</span>' +
             '<span class="t-bar"><i style="width:' + p + '%"></i></span>' +
             '<span class="t-c">' + ok + '/' + list.length + '</span></button>';
    }).join('');
    $$('.topic', $('#topics')).forEach(function (el) {
      el.addEventListener('click', function () { start('topic', el.getAttribute('data-topic')); });
    });
  }

  /* ------------------------------------------------------------------ связи */

  $('#mode-quick').addEventListener('click', function () { start('quick'); });
  $('#mode-exam').addEventListener('click', function () { start('exam'); });
  $('#mode-missed').addEventListener('click', function () { start('missed'); });

  $('#act-main').addEventListener('click', function () {
    var it = run.items[run.pos];
    if (it.checked) { next(); } else { check(); }
  });
  $('#act-skip').addEventListener('click', skip);

  /* Ссылка из курса: quiz.html#chapter/<раздел>. Так со страницы раздела
     попадаешь сразу к его вопросам, а не к общему выбору набора. */
  function fromHash() {
    var raw = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    if (!raw) { return false; }
    var bits = raw.split('/');
    if (bits[0] === 'chapter' && CHAPTER[bits[1]]) { start('chapter', bits[1]); return true; }
    if (bits[0] === 'topic' && TOPIC[bits[1]]) { start('topic', bits[1]); return true; }
    return false;
  }

  function toStart() {
    if (location.hash) { history.replaceState(null, '', location.pathname + location.search); }
    paintStart();
    show('start');
  }

  $('#to-start').addEventListener('click', toStart);
  window.addEventListener('hashchange', function () { if (!fromHash()) { toStart(); } });
  $('#again').addEventListener('click', function () { start(run.mode, run.arg); });
  $('#again-missed').addEventListener('click', function () { start('missed'); });

  $('#reset').addEventListener('click', function () {
    if (!window.confirm('Сбросить всю статистику ответов?')) { return; }
    store = { stats: {} };
    save(store);
    paintStart();
  });

  document.addEventListener('keydown', function (e) {
    if ($('#screen-run').hidden) { return; }
    if (e.target && /^(INPUT|TEXTAREA)$/.test(e.target.tagName)) { return; }
    if (e.key === 'Enter') {
      if (!$('#act-main').disabled) { e.preventDefault(); $('#act-main').click(); }
      return;
    }
    if (/^[1-9]$/.test(e.key)) {
      var el = $('.opt[data-i="' + (+e.key - 1) + '"]', $('#opts'));
      if (el && !el.disabled) { e.preventDefault(); el.click(); }
    }
  });

  /* ------------------------------------------------------------------- тема */

  $('#theme-btn').addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.getAttribute('data-theme') === 'dark'
      || (!root.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY_THEME, next); } catch (e) {}
  });

  paintStart();
  fromHash();
})();
