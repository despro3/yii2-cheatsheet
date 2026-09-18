/* Справочник Yii 2 — навигация по каталогу и живые демонстрации. */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватный режим */ } }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  /* --------------------------------------------------------------------------- тема */

  var themeBtn = $('#theme-btn');

  function applyTheme(mode) {
    if (mode === 'dark' || mode === 'light') root.setAttribute('data-theme', mode);
    else root.removeAttribute('data-theme');
  }
  applyTheme(read('yii-explorer:theme'));

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = root.getAttribute('data-theme');
      var dark = current === 'dark' || (!current && window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);
      var next = dark ? 'light' : 'dark';
      applyTheme(next);
      store('yii-explorer:theme', next);
    });
  }

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
    el.addEventListener('click', function (e) {
      e.preventDefault();
      openTopic(el.getAttribute('data-open'));
    });
  });

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

  $$('.ref-block').forEach(function (block) {
    var input = $('.ref-search input', block);
    var count = $('.ref-count', block);
    var items = $$('.ref-item', block);
    var empty = $('.ref-empty', block);
    var total = items.length;

    items.forEach(function (item) {
      var btn = $('.ref-btn', item);
      btn.addEventListener('click', function () {
        var open = !item.classList.contains('open');
        item.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        $('.ref-body', item).hidden = !open;
      });
    });

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
    });
  });

  /* --------------------------------------------------------------------------- демо */

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* --------------------------------------------------------------------------- демо 1: проверка валидаторами вживую */

  var VALIDATORS = {
    required: {
      label: 'required — обязательно',
      opts: [],
      msg: 'Необходимо заполнить «значение».',
      neverSkips: true,
      run: function (v) { return v !== '' && v !== null; }
    },
    string: {
      label: 'string — строка',
      opts: [{ k: 'min', ph: 'мин. длина', v: '3' }, { k: 'max', ph: 'макс. длина', v: '10' }],
      run: function (v, o) {
        var n = Array.from(v).length;
        if (o.min && n < +o.min) return 'Значение должно содержать минимум ' + o.min + ' символа.';
        if (o.max && n > +o.max) return 'Значение должно содержать максимум ' + o.max + ' символов.';
        return true;
      }
    },
    integer: {
      label: 'integer — целое число',
      opts: [{ k: 'min', ph: 'минимум', v: '18' }, { k: 'max', ph: 'максимум', v: '' }],
      run: function (v, o) {
        if (!/^[+-]?\d+$/.test(v)) return 'Значение должно быть целым числом.';
        var n = parseInt(v, 10);
        if (o.min !== '' && n < +o.min) return 'Значение должно быть не меньше ' + o.min + '.';
        if (o.max !== '' && n > +o.max) return 'Значение должно быть не больше ' + o.max + '.';
        return true;
      }
    },
    number: {
      label: 'number — любое число',
      opts: [{ k: 'min', ph: 'минимум', v: '0' }, { k: 'max', ph: 'максимум', v: '' }],
      run: function (v, o) {
        if (!/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(v)) return 'Значение должно быть числом.';
        var n = parseFloat(v);
        if (o.min !== '' && n < +o.min) return 'Значение должно быть не меньше ' + o.min + '.';
        if (o.max !== '' && n > +o.max) return 'Значение должно быть не больше ' + o.max + '.';
        return true;
      }
    },
    email: {
      label: 'email — адрес почты',
      opts: [],
      run: function (v) {
        return /^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/.test(v) ? true : 'Значение не является правильным email адресом.';
      }
    },
    url: {
      label: 'url — адрес страницы',
      opts: [{ k: 'defaultScheme', ph: 'схема по умолчанию', v: 'https' }],
      run: function (v, o) {
        var s = v;
        var added = false;
        if (o.defaultScheme && !/^[a-z][a-z0-9+.-]*:\/\//i.test(s)) { s = o.defaultScheme + '://' + s; added = true; }
        var ok = /^[a-z][a-z0-9+.-]*:\/\/[^\s/?#]+\.[^\s/?#]+/i.test(s);
        if (!ok) return 'Значение не является правильным URL.';
        return added ? { ok: true, note: 'схема дописана: ' + s } : true;
      }
    },
    match: {
      label: 'match — регулярное выражение',
      opts: [{ k: 'pattern', ph: 'шаблон', v: '/^[a-z]\\w*$/i' }],
      run: function (v, o) {
        var m = /^\/(.*)\/([a-z]*)$/.exec(o.pattern || '');
        if (!m) return 'Шаблон нужно записать как /выражение/флаги.';
        var re;
        try { re = new RegExp(m[1], m[2]); } catch (e) { return 'Неверное регулярное выражение.'; }
        return re.test(v) ? true : 'Значение неверно.';
      }
    },
    'in': {
      label: 'in — из списка',
      opts: [{ k: 'range', ph: 'через запятую', v: 'draft, review, published' }],
      run: function (v, o) {
        var list = String(o.range || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean);
        return list.indexOf(v) >= 0 ? true : 'Значения «значение» нет в списке допустимых.';
      }
    },
    compare: {
      label: 'compare — сравнение',
      opts: [
        { k: 'compareValue', ph: 'с чем сравнить', v: '100' },
        { k: 'operator', ph: '>=', v: '>=' },
        { k: 'type', ph: 'string | number', v: 'number' }
      ],
      run: function (v, o) {
        var a = v, b = o.compareValue;
        if (o.type === 'number') { a = parseFloat(a); b = parseFloat(b); if (isNaN(a)) return 'Значение должно быть числом.'; }
        var ops = {
          '==': a == b, '===': a === b, '!=': a != b, '!==': a !== b,
          '>': a > b, '>=': a >= b, '<': a < b, '<=': a <= b
        };
        if (!(o.operator in ops)) return 'Оператор должен быть одним из ==, ===, !=, !==, >, >=, <, <=.';
        if (ops[o.operator]) return true;
        return o.type === 'number'
          ? 'Значение должно быть ' + o.operator + ' ' + o.compareValue + '.'
          : 'Сравнение строк: «' + v + '» ' + o.operator + ' «' + o.compareValue + '» не выполняется.';
      }
    },
    boolean: {
      label: 'boolean — логическое',
      opts: [],
      run: function (v) {
        return (v === '1' || v === '0') ? true : 'Значение должно быть «1» или «0» (trueValue и falseValue).';
      }
    },
    date: {
      label: 'date — дата',
      opts: [{ k: 'format', ph: 'php:d.m.Y', v: 'php:d.m.Y' }],
      run: function (v, o) {
        var f = String(o.format || '').replace(/^php:/, '');
        var seps = { 'd.m.Y': /^(\d{2})\.(\d{2})\.(\d{4})$/, 'Y-m-d': /^(\d{4})-(\d{2})-(\d{2})$/ };
        var re = seps[f];
        if (!re) return 'В демонстрации поддержаны форматы php:d.m.Y и php:Y-m-d.';
        var m = re.exec(v);
        if (!m) return 'Значение не является правильной датой.';
        var y = f === 'Y-m-d' ? +m[1] : +m[3];
        var mo = +m[2];
        var d = f === 'Y-m-d' ? +m[3] : +m[1];
        var dt = new Date(Date.UTC(y, mo - 1, d));
        var real = dt.getUTCFullYear() === y && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === d;
        if (!real) return 'Такой даты не существует.';
        return { ok: true, note: 'timestamp: ' + Math.floor(dt.getTime() / 1000) };
      }
    },
    trim: {
      label: 'trim — обрезать пробелы',
      opts: [],
      isFilter: true,
      run: function (v) { return { ok: true, note: 'значение станет: «' + v.trim() + '»' }; }
    }
  };

  function initValidatorLab(el) {
    var sel = $('#vl-kind', el);
    var optsBox = $('#vl-opts', el);
    var valInput = $('#vl-value', el);
    var skipBox = $('#vl-skip', el);
    var verdict = $('#vl-verdict', el);
    var ruleOut = $('#vl-rule', el);

    Object.keys(VALIDATORS).forEach(function (key) {
      var o = document.createElement('option');
      o.value = key; o.textContent = VALIDATORS[key].label;
      sel.appendChild(o);
    });
    sel.value = 'string';

    function buildOpts() {
      var spec = VALIDATORS[sel.value];
      optsBox.innerHTML = '';
      optsBox.hidden = spec.opts.length === 0;
      spec.opts.forEach(function (opt) {
        var wrap = document.createElement('div');
        wrap.className = 'field';
        wrap.innerHTML = '<label for="vl-o-' + opt.k + '">' + esc(opt.k) + '</label>' +
          '<input type="text" id="vl-o-' + opt.k + '" data-opt="' + esc(opt.k) + '" ' +
          'value="' + esc(opt.v) + '" placeholder="' + esc(opt.ph) + '">';
        optsBox.appendChild(wrap);
        $('input', wrap).addEventListener('input', run);
      });
    }

    function readOpts() {
      var o = {};
      $$('[data-opt]', optsBox).forEach(function (i) { o[i.getAttribute('data-opt')] = i.value; });
      return o;
    }

    function ruleLine(kind, opts) {
      var parts = ["'значение'", "'" + kind + "'"];
      Object.keys(opts).forEach(function (k) {
        var v = opts[k];
        if (v === '') return;
        var num = /^-?\d+(\.\d+)?$/.test(v) && k !== 'pattern' && k !== 'format' && k !== 'operator' && k !== 'type';
        if (k === 'range') {
          var list = v.split(',').map(function (x) { return "'" + x.trim() + "'"; }).filter(function (x) { return x !== "''"; });
          parts.push("'range' => [" + list.join(', ') + ']');
        } else {
          parts.push("'" + k + "' => " + (num ? v : "'" + v + "'"));
        }
      });
      if (!skipBox.checked) parts.push("'skipOnEmpty' => false");
      return '[' + parts.join(', ') + '],';
    }

    function run() {
      var kind = sel.value;
      var spec = VALIDATORS[kind];
      var value = valInput.value;
      var opts = readOpts();

      ruleOut.textContent = ruleLine(kind, opts);

      var empty = value === '';
      if (empty && !spec.neverSkips && skipBox.checked) {
        verdict.className = 'verdict';
        verdict.innerHTML = '<b>правило пропущено</b><span class="vtext">значение пустое, а skipOnEmpty включён. ' +
          'Именно поэтому «пустое поле прошло проверку» — самая частая неожиданность в Yii.</span>';
        return;
      }

      var res = spec.run(value, opts);
      var ok = res === true || (res && res.ok);
      var note = res && res.note ? res.note : '';
      var message = ok ? '' : (typeof res === 'string' ? res : (spec.msg || 'Значение неверно.'));

      verdict.className = 'verdict ' + (ok ? 'pass' : 'fail');
      verdict.innerHTML = ok
        ? '<b>проходит</b><span class="vtext">' + (note ? esc(note) : (spec.isFilter ? '' : 'validate() вернёт true')) + '</span>'
        : '<b>не проходит</b><span class="vtext">' + esc(message) + '</span>';
    }

    sel.addEventListener('change', function () { buildOpts(); run(); });
    valInput.addEventListener('input', run);
    skipBox.addEventListener('change', run);
    buildOpts();
    run();
  }

  /* --------------------------------------------------------------------------- демо 2: что даёт выбранный сценарий */

  var SC_RULES = [
    { attrs: ['username', 'email'], rule: 'required', on: null, except: null },
    { attrs: ['email'], rule: 'email', on: null, except: null },
    { attrs: ['email'], rule: 'unique', on: null, except: ['update'] },
    { attrs: ['password'], rule: 'required', on: ['register'], except: null },
    { attrs: ['captcha'], rule: 'captcha', on: ['register'], except: null },
    { attrs: ['about'], rule: 'string', on: ['profile'], except: null },
    { attrs: ['role'], rule: 'in', on: ['admin'], except: null }
  ];
  var SC_SCENARIOS = ['default', 'register', 'profile', 'update', 'admin'];
  var SC_ATTRS = ['username', 'email', 'password', 'captcha', 'about', 'role'];
  // в сценарии admin роль проверяется, но не присваивается массово
  var SC_UNSAFE = { admin: ['role'] };

  function initScenarioLab(el) {
    var chips = $$('.chip', el);
    var table = $('#sl-table', el);
    var hint = $('#sl-hint', el);
    var scenario = 'default';

    function activeFor(sc) {
      var set = {};
      SC_RULES.forEach(function (r) {
        var on = !r.on || r.on.indexOf(sc) >= 0;
        var ex = r.except && r.except.indexOf(sc) >= 0;
        if (on && !ex) r.attrs.forEach(function (a) { set[a] = true; });
      });
      return set;
    }

    function render() {
      var active = activeFor(scenario);
      var unsafe = SC_UNSAFE[scenario] || [];
      var rows = SC_ATTRS.map(function (a) {
        var isActive = !!active[a];
        var isSafe = isActive && unsafe.indexOf(a) < 0;
        return '<div class="kv-row">' +
          '<div class="kv-k">' + esc(a) + '</div>' +
          '<div class="kv-v">' +
            '<span class="tagl ' + (isActive ? 'yes' : 'no') + '">' + (isActive ? 'проверяется' : 'правил нет') + '</span> ' +
            '<span class="tagl ' + (isSafe ? 'yes' : 'no') + '">' + (isSafe ? 'придёт из load()' : 'load() пропустит') + '</span>' +
          '</div></div>';
      }).join('');
      table.innerHTML = rows;

      var n = Object.keys(active).length;
      hint.textContent = scenario === 'admin'
        ? 'В scenarios() роль записана как «!role»: правило работает, но через load() значение не пройдёт — подделать роль из формы нельзя.'
        : 'Активных атрибутов: ' + n + ' из ' + SC_ATTRS.length + '. Остальные load() просто не присвоит, молча.';
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        scenario = chip.getAttribute('data-sc');
        chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        render();
      });
    });
    render();
  }

  /* --------------------------------------------------------------------------- демо 3: жизненный цикл сохранения записи */

  var LC = {
    insert: [
      ['beforeValidate()', 'EVENT_BEFORE_VALIDATE', 'Можно поправить данные перед проверкой. Возврат false отменяет всё.'],
      ['проверка правил', 'rules()', 'Работают правила активного сценария. Не прошло — save() вернёт false, запросов к базе не будет.'],
      ['afterValidate()', 'EVENT_AFTER_VALIDATE', 'Проверка закончена, ошибки уже известны.'],
      ['beforeSave(true)', 'EVENT_BEFORE_INSERT', 'Сюда встроен TimestampBehavior: заполняет created_at и updated_at. И BlameableBehavior: автора.', 'hook'],
      ['INSERT', 'запрос к базе', 'Уходят все атрибуты. Первичный ключ возвращается в модель.'],
      ['afterSave(true, [])', 'EVENT_AFTER_INSERT', 'Здесь ставят задачи в очередь и сбрасывают кэш. $changedAttributes пуст: запись новая.', 'hook']
    ],
    update: [
      ['beforeValidate()', 'EVENT_BEFORE_VALIDATE', 'То же, что и при вставке.'],
      ['проверка правил', 'rules()', 'Проверяются все атрибуты сценария, а не только изменённые.'],
      ['afterValidate()', 'EVENT_AFTER_VALIDATE', ''],
      ['beforeSave(false)', 'EVENT_BEFORE_UPDATE', 'TimestampBehavior обновляет только updated_at.', 'hook'],
      ['UPDATE', 'запрос к базе', 'В запрос попадут ТОЛЬКО изменённые атрибуты. Если их нет, запроса не будет вовсе и save() вернёт 0.'],
      ['afterSave(false, $changed)', 'EVENT_AFTER_UPDATE', '$changedAttributes хранит старые значения: можно сравнить «было и стало».', 'hook']
    ],
    'delete': [
      ['beforeDelete()', 'EVENT_BEFORE_DELETE', 'Последняя возможность запретить удаление: верните false.'],
      ['DELETE', 'запрос к базе', 'Удаляется одна строка по первичному ключу.'],
      ['afterDelete()', 'EVENT_AFTER_DELETE', 'Чистят связанные файлы и кэш.', 'hook']
    ],
    find: [
      ['конструктор', '', 'Объект создан, атрибуты ещё пусты.'],
      ['init()', 'EVENT_INIT', 'Общая инициализация, ещё до данных.'],
      ['заполнение атрибутов', '', 'Значения из строки таблицы приводятся к типам по схеме.'],
      ['afterFind()', 'EVENT_AFTER_FIND', 'Здесь разворачивают JSON-поля и считают производные значения.', 'hook']
    ]
  };

  function initLifecycleLab(el) {
    var chips = $$('.chip', el);
    var list = $('#lc-list', el);
    var note = $('#lc-note', el);
    var playBtn = $('#lc-play', el);
    var mode = 'insert';
    var timer = null;

    function render(activeIndex) {
      var steps = LC[mode];
      list.innerHTML = steps.map(function (s, i) {
        var mods = [];
        if (s[3] === 'hook') mods.push('hook');
        if (activeIndex === i) mods.push('on');
        else if (activeIndex !== null && i < activeIndex) mods.push('done');
        return '<div class="lc-step' + (mods.length ? ' ' + mods.join(' ') : '') + '" data-i="' + i + '">' +
          '<span class="lc-i">' + (i + 1) + '</span>' +
          '<span class="lc-n">' + esc(s[0]) + '</span>' +
          '<span class="lc-t">' + esc(s[1]) + '</span>' +
        '</div>';
      }).join('');
      if (activeIndex === null) {
        note.textContent = 'Нажмите «Выполнить», чтобы пройти цепочку шаг за шагом. Слева цветной полосой отмечены точки, куда встраиваются поведения.';
      } else {
        note.textContent = steps[activeIndex][2] || '';
      }
    }

    function play() {
      if (timer) { clearInterval(timer); timer = null; }
      var steps = LC[mode];
      var i = 0;
      playBtn.disabled = true;
      render(0);
      timer = setInterval(function () {
        i++;
        if (i >= steps.length) {
          clearInterval(timer); timer = null;
          playBtn.disabled = false;
          render(steps.length - 1);
          return;
        }
        render(i);
      }, 900);
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        mode = chip.getAttribute('data-lc');
        chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        if (timer) { clearInterval(timer); timer = null; playBtn.disabled = false; }
        render(null);
      });
    });
    list.addEventListener('click', function (e) {
      var row = e.target.closest('.lc-step');
      if (!row) return;
      if (timer) { clearInterval(timer); timer = null; playBtn.disabled = false; }
      render(+row.getAttribute('data-i'));
    });
    playBtn.addEventListener('click', play);
    render(null);
  }

  /* --------------------------------------------------------------------------- демо 4: из конструктора запроса в SQL */

  var QB = [
    { k: 'status', label: 'where(status)', php: "->where(['status' => Post::STATUS_PUBLISHED])", sql: 'WHERE `status` = 1' },
    { k: 'like', label: "andWhere(like title)", php: "->andWhere(['like', 'title', 'yii'])", sql: "AND `title` LIKE '%yii%'" },
    { k: 'filter', label: 'andFilterWhere(пусто)', php: "->andFilterWhere(['author_id' => null])", sql: '', note: 'Пустое значение — условие не добавлено. В этом весь смысл filterWhere.' },
    { k: 'in', label: 'andWhere(in tag_id)', php: "->andWhere(['in', 'tag_id', [3, 7]])", sql: 'AND `tag_id` IN (3, 7)' },
    { k: 'join', label: 'joinWith(author)', php: "->joinWith('author')", sql: 'LEFT JOIN `user` ON `user`.`id` = `post`.`author_id`', join: true },
    { k: 'joinwhere', label: 'where по author', php: "->andWhere(['user.status' => 1])", sql: 'AND `user`.`status` = 1', needs: 'join' },
    { k: 'with', label: "with(tags)", php: "->with('tags')", sql: '', note: 'with() не добавляет JOIN: связь загрузится отдельным запросом SELECT * FROM tag WHERE id IN (…).' },
    { k: 'group', label: 'groupBy(post.id)', php: "->groupBy('post.id')", sql: 'GROUP BY `post`.`id`' },
    { k: 'order', label: 'orderBy(created_at)', php: "->orderBy(['created_at' => SORT_DESC])", sql: 'ORDER BY `created_at` DESC' },
    { k: 'limit', label: 'limit(10)', php: '->limit(10)', sql: 'LIMIT 10' }
  ];

  function initQueryLab(el) {
    var chips = $$('.chip', el);
    var phpOut = $('#ql-php', el);
    var sqlOut = $('#ql-sql', el);
    var noteOut = $('#ql-note', el);
    var on = { status: true, order: true, limit: true };

    function render() {
      var php = ['Post::find()'];
      var joins = [], wheres = [], group = '', order = '', limit = '';
      var notes = [];

      QB.forEach(function (item) {
        if (!on[item.k]) return;
        if (item.needs && !on[item.needs]) return;
        php.push('    ' + item.php);
        if (item.note) notes.push(item.note);
        if (!item.sql) return;
        if (item.join) joins.push(item.sql);
        else if (item.sql.indexOf('GROUP BY') === 0) group = item.sql;
        else if (item.sql.indexOf('ORDER BY') === 0) order = item.sql;
        else if (item.sql.indexOf('LIMIT') === 0) limit = item.sql;
        else wheres.push(item.sql);
      });
      php.push('    ->all();');
      phpOut.textContent = php.join('\n');

      var sql = ['SELECT `post`.* FROM `post`'];
      joins.forEach(function (j) { sql.push(j); });
      if (wheres.length) {
        var first = wheres[0].replace(/^AND /, '');
        sql.push(first.indexOf('WHERE') === 0 ? first : 'WHERE ' + first);
        wheres.slice(1).forEach(function (w) { sql.push('  ' + (w.indexOf('AND ') === 0 ? w : 'AND ' + w)); });
      }
      if (group) sql.push(group);
      if (order) sql.push(order);
      if (limit) sql.push(limit);
      sqlOut.textContent = sql.join('\n');

      noteOut.innerHTML = notes.length ? notes.map(esc).join(' ') : '';
      noteOut.hidden = notes.length === 0;

      chips.forEach(function (c) {
        var k = c.getAttribute('data-q');
        var item = QB.filter(function (i) { return i.k === k; })[0];
        var blocked = item && item.needs && !on[item.needs];
        c.setAttribute('aria-pressed', on[k] ? 'true' : 'false');
        c.disabled = !!blocked;
        c.style.opacity = blocked ? '.45' : '';
      });
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var k = chip.getAttribute('data-q');
        on[k] = !on[k];
        render();
      });
    });
    render();
  }

  /* --------------------------------------------------------------------------- запуск всех демо */

  var DEMOS = {
    'validator-lab': initValidatorLab,
    'scenario-lab': initScenarioLab,
    'lifecycle-lab': initLifecycleLab,
    'query-lab': initQueryLab
  };

  $$('[data-demo]').forEach(function (el) {
    var fn = DEMOS[el.getAttribute('data-demo')];
    if (!fn) return;
    try { fn(el); } catch (e) { if (window.console) console.error('демо не запустилось:', el.getAttribute('data-demo'), e); }
  });

  /* стартовое состояние из адреса */
  fromHash(false);
})();
