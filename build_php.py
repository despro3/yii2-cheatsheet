# -*- coding: utf-8 -*-
"""Сборка страницы «Справочник PHP 8+» из src/php/.

    python3 build_php.py

Пишет два файла:
    docs/php.html            самостоятельная страница (открывается из файла)
    src/php/_fragment.html   та же страница без обвязки, для публикации

Таблицы для двух демонстраций считает сам PHP — см. src/php/data/gen.php.
Пересобирать их нужно, только если менялись списки значений и типов.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'php')
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, ROOT)

import build as site                      # noqa: E402  подсветка кода из основной сборки
import catalog                            # noqa: E402  общий движок справочников
import content as data                    # noqa: E402
from catalog import attr, esc, node       # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'php.html')
FRAGMENT = os.path.join(SRC, '_fragment.html')

TITLE = 'Справочник PHP 8+'
DESCRIPTION = ('Каталог возможностей PHP 8.0–8.5: карточки механизмов языка, полные списки '
               'встроенного с отметкой версии и живые демонстрации.')

GROUP_COLOR = {
    'exec': 'var(--g-exec)',
    'val':  'var(--g-val)',
    'fn':   'var(--g-fn)',
    'oop':  'var(--g-oop)',
    'lib':  'var(--g-lib)',
    'eco':  'var(--g-eco)',
}

# Подсветка приехала из сборки курса, где PHP — язык примеров, а не тема.
# Здесь в коде встречаются и объявления типов, и never, и exit — добавляем их,
# иначе половина примеров этой страницы осталась бы серой.
EXTRA_KEYWORDS = 'int float string bool void never mixed iterable object exit die from'.split()
site.LANG_RULES['php'] = [(cls, site._alt(site.PHP_KEYWORDS + EXTRA_KEYWORDS) if cls == 'kw' else pat)
                          for cls, pat in site.LANG_RULES['php']]


# --------------------------------------------------------------------------- демонстрации

DEMOS = {}


def demo(name):
    def wrap(fn):
        DEMOS[name] = fn
        return fn
    return wrap


@demo('compare-lab')
def demo_compare():
    return '''<div class="demo" data-demo="compare-lab">
  <div class="demo-head"><span class="dot"></span>сравните два значения</div>
  <div class="demo-body">
    <div class="field"><label>слева</label><div class="chips" data-role="a"></div></div>
    <div class="field"><label>справа</label><div class="chips" data-role="b"></div></div>
    <div class="verdict" data-role="verdict"></div>
    <div class="tt-wrap"><table class="tt" data-role="table"></table></div>
    <p class="demo-note" data-role="note"></p>
  </div>
</div>'''


@demo('types-lab')
def demo_types():
    return '''<div class="demo" data-demo="types-lab">
  <div class="demo-head"><span class="dot"></span>что сделает объявленный тип</div>
  <div class="demo-body">
    <div class="row2">
      <div class="field"><label for="tl-type">тип параметра</label><select id="tl-type"></select></div>
      <div class="field"><label for="tl-value">переданное значение</label><select id="tl-value"></select></div>
    </div>
    <div><div class="out-label">проверяемый вызов</div><pre class="out" data-role="call"></pre></div>
    <div class="row2">
      <div class="verdict" data-role="weak"></div>
      <div class="verdict" data-role="strict"></div>
    </div>
    <p class="demo-note" data-role="note"></p>
  </div>
</div>'''


@demo('bytes-lab')
def demo_bytes():
    return '''<div class="demo" data-demo="bytes-lab">
  <div class="demo-head"><span class="dot"></span>строка — это байты</div>
  <div class="demo-body">
    <div class="field"><label for="bl-input">строка</label>
      <input type="text" id="bl-input" value="Привет, PHP!"></div>
    <div class="chips" data-role="samples"></div>
    <div class="kv" data-role="table"></div>
    <div><div class="out-label">по байтам и по символам</div><div class="bytes" data-role="split"></div></div>
    <p class="demo-note" data-role="note"></p>
  </div>
</div>'''


@demo('version-lab')
def demo_version():
    return '''<div class="demo" data-demo="version-lab">
  <div class="demo-head"><span class="dot"></span>что даёт версия</div>
  <div class="demo-body">
    <div class="chips" data-role="vers"></div>
    <div class="verdict" data-role="head"></div>
    <div class="kv" data-role="added"></div>
    <p class="demo-note" data-role="note"></p>
  </div>
</div>'''


render_block = catalog.make_render(DEMOS)


# --------------------------------------------------------------------------- схема-карта

def build_map():
    C = GROUP_COLOR
    by_id = {t['id']: t for t in data.TOPICS}

    def tip(tid):
        t = by_id[tid]
        return {'title': t['title'], 'cls': t['cls'], 'badge': t['badge'], 'lead': t['lead']}

    p = []
    p.append('<svg viewBox="0 0 1060 836" role="img" class="mp" '
             'aria-label="Устройство PHP: сверху путь кода от запуска и настройки через компиляцию '
             'в опкоды и их кэш к выполнению и выводу; выполнение опирается на автозагрузку классов '
             'и обработку ошибок; ниже четыре семейства возможностей языка, которые код дёргает; '
             'внизу то, без чего на PHP не пишут">')
    p.append('<defs><marker id="mp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" class="mp-head"/></marker></defs>')

    # фундамент
    p.append('<rect class="mp-slab" x="30" y="668" width="1000" height="140" rx="12" stroke-dasharray="5 4"/>')
    p.append('<text class="mp-label" style="fill: %s" x="530" y="694" text-anchor="middle">'
             'вокруг языка · без этого на PHP не пишут</text>' % C['eco'])

    # путь кода: слева направо, ровно в том порядке, в каком PHP проходит его сам
    path = [
        (46, 196, 'запуск', 'SAPI и php.ini', 'runtime', C['exec'], ''),
        (262, 170, 'компиляция', 'файл → опкоды', None, None, ''),
        (452, 180, 'опкоды', 'OPcache хранит их', None, None, 'mp-io'),
        (652, 180, 'выполнение', 'Zend VM', None, None, ''),
        (852, 160, 'вывод', 'echo, заголовки', None, None, 'mp-io'),
    ]
    for x, w, label, sub, tid, color, cls in path:
        p.append(node(x, 28, w, 56, label, sub, tid, color, cls, tip(tid) if tid else None))

    p.append('<g class="mp-flow" marker-end="url(#mp-a)">')
    for a, b in zip(path, path[1:]):
        gap_from = a[0] + a[1] + 5
        p.append('<path d="M%d 56h%d"/>' % (gap_from, b[0] - 7 - gap_from))
    p.append('</g>')

    # из выполнения вниз: слева два механизма, которыми оно занято постоянно,
    # прямо вниз — шина к семействам возможностей
    p.append('<g class="mp-flow"><path d="M742 84v34H144"/></g>')
    p.append('<g class="mp-flow" marker-end="url(#mp-a)">'
             '<path d="M144 118v12"/><path d="M360 118v12"/></g>')
    p.append(node(46, 130, 196, 58, 'автозагрузка', 'класс по имени файла',
                  'autoload', C['exec'], '', tip('autoload')))
    p.append(node(262, 130, 196, 58, 'ошибки', 'исключения и Throwable',
                  'errors', C['exec'], '', tip('errors')))

    # семейства: колонка на семейство, порядок строк — от простого к редкому
    columns = [
        ('значения', C['val'], ['types', 'operators', 'strings', 'arrays'],
         ['типы и приведение', 'операторы', 'строки', 'массивы']),
        ('функции', C['fn'], ['functions', 'closures', 'generators', 'fibers'],
         ['функции и аргументы', 'замыкания', 'генераторы', 'файберы']),
        ('объекты', C['oop'], ['classes', 'props', 'interfaces', 'traits', 'enums', 'magic'],
         ['классы', 'свойства', 'интерфейсы', 'трейты', 'перечисления', 'магические методы']),
        ('стандартная библиотека', C['lib'], ['datetime', 'json', 'regex', 'files', 'spl'],
         ['дата и время', 'JSON', 'регулярные выражения', 'файлы и потоки', 'SPL']),
    ]
    cx0, cw, cstep = 46, 236, 252
    centers = [cx0 + i * cstep + cw / 2.0 for i in range(len(columns))]

    # шина: выполнение тянется к каждому семейству
    p.append('<g class="mp-flow">')
    p.append('<path d="M742 84v134"/>')
    p.append('<path d="M%g 218H%g"/>' % (centers[0], max(centers[-1], 742)))
    p.append('</g>')
    p.append('<g class="mp-flow" marker-end="url(#mp-a)">')
    for c in centers:
        p.append('<path d="M%g 218v12"/>' % c)
    p.append('</g>')

    for i, (label, color, ids, labels) in enumerate(columns):
        p.append('<text class="mp-label" style="fill: %s" x="%g" y="250" text-anchor="middle">%s</text>'
                 % (color, centers[i], label))
        for row, (tid, name) in enumerate(zip(ids, labels)):
            p.append(node(cx0 + i * cstep, 262 + row * 68, cw, 56,
                          name, by_id[tid]['badge'], tid, color, '', tip(tid)))

    # фундамент: узлы
    base = [('attributes', 'атрибуты'), ('composer', 'Composer'), ('psr', 'PSR'),
            ('tools', 'инструменты'), ('versions', 'версии 8.0–8.5')]
    for i, (tid, name) in enumerate(base):
        p.append(node(48 + i * 196, 714, 180, 60, name, by_id[tid]['badge'],
                      tid, C['eco'], '', tip(tid)))

    p.append('</svg>')
    return ''.join(p)


# --------------------------------------------------------------------------- страница

def build_page():
    css = open(os.path.join(SRC, 'php.css'), encoding='utf-8').read()
    js = open(os.path.join(SRC, 'php.js'), encoding='utf-8').read()

    refs = sum(len(b[1]) for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'ref')

    # быстрый режим открывает вкладку со списком встроенного; проверяем, что она у всех одна и та же
    quick_tabs = {t['tabs'][1][0] for t in data.TOPICS if len(t['tabs']) > 1}
    assert len(quick_tabs) == 1, 'вторая вкладка называется по-разному: %s' % sorted(quick_tabs)
    quick_tab = quick_tabs.pop()
    assert all(any(b[0] == 'ref' for b in t['tabs'][1][2]) for t in data.TOPICS), \
        'на второй вкладке не у всех узлов есть список'

    tables = {
        'compare': json.load(open(os.path.join(SRC, 'data', 'compare.json'), encoding='utf-8')),
        'types': json.load(open(os.path.join(SRC, 'data', 'types.json'), encoding='utf-8')),
        'versions': data.VERSIONS,
    }

    head = '''<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
%s
</style>''' % (esc(TITLE), css)

    body = '''<header class="top">
  <div class="top-in">
    <span class="mark"><b>PHP</b><span class="mark-text">Справочник PHP 8+</span></span>
    <span class="top-count">%d узлов · %d возможностей</span>
    <span class="top-spacer"></span>
    <span class="learned" id="learned" hidden>изучено <b id="learned-n">0</b> из %d<button
      type="button" id="learned-reset">сбросить</button></span>
    <button type="button" class="pill-btn" id="quick-btn" aria-pressed="false" data-tab="%s"
      title="Открывать узел сразу на списке встроенного">сразу к списку</button>
    <a class="back-link" href="index.html">на главную</a>
    <button type="button" class="icon-btn" id="theme-btn" aria-label="Переключить тему">
      <svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
      <svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
</header>

<main>
  <div class="wrap">
    <section class="map">
      <figure>
        <div class="map-frame">%s</div>
        <figcaption>Сверху — путь кода: PHP поднимается, компилирует файл в опкоды, держит их
          в кэше и выполняет. Ниже — четыре семейства возможностей, которые этот код дёргает,
          а внизу то, без чего на PHP всё равно не пишут. Нажмите на блок, чтобы открыть разбор;
          при наведении мышью — короткая справка.</figcaption>
      </figure>
    </section>

    %s
  </div>
</main>

<div class="scrim" id="scrim" hidden></div>
<div class="panel" id="panel" role="dialog" aria-modal="true" aria-label="Разбор узла" hidden>
  <div class="panel-bar">
    <span class="pb-title" id="pb-title"></span>
    <span class="sp"></span>
    <label class="learn-box"><input type="checkbox" id="learn-check"> изучено</label>
    <kbd>Esc</kbd>
    <button type="button" class="icon-btn" id="panel-close" aria-label="Закрыть">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
  <div class="panel-body"><div class="panel-body-in" id="panel-body-in"></div></div>
</div>

<div id="topic-store" hidden>%s</div>

<div class="tip" id="tip" role="tooltip" hidden></div>

<script>
/* таблицы сравнения и проверки типов посчитал сам PHP: src/php/data/gen.php */
window.PHPREF = %s;
</script>
<script>
%s
</script>''' % (len(data.TOPICS), refs, len(data.TOPICS), quick_tab,
                build_map(), catalog.build_index(data.GROUPS, data.TOPICS, GROUP_COLOR),
                catalog.build_topics(data.TOPICS, GROUP_COLOR, render_block),
                json.dumps(tables, ensure_ascii=False, separators=(',', ':')), js)

    return head, body


def main():
    head, body = build_page()
    size = catalog.write_page(OUT, FRAGMENT, TITLE, DESCRIPTION, head, body)

    print('Узлов: %d, справочных записей: %d, демонстраций: %d'
          % (len(data.TOPICS),
             sum(len(b[1]) for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'ref'),
             sum(1 for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'demo')))
    print('Готово: %s (%.0f КБ)' % (OUT, size / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
