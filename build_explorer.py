# -*- coding: utf-8 -*-
"""Сборка страницы «Разборный Yii 2» из src/explorer/.

    python3 build_explorer.py

Пишет два файла:
    docs/explorer.html            самостоятельная страница (открывается из файла)
    src/explorer/_fragment.html   та же страница без обвязки, для публикации
"""

import html as html_mod
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'explorer')
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

import build as site                      # noqa: E402  подсветка кода из основной сборки
import content as data                    # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'explorer.html')
FRAGMENT = os.path.join(SRC, '_fragment.html')

TITLE = 'Разборный Yii 2'
DESCRIPTION = ('Каталог механизмов Yii 2: карточки основных узлов фреймворка, '
               'полные списки встроенного и живые демонстрации.')

# числительное для лида: счёт узлов берётся из данных, а строка должна читаться словами
NUMERALS = {
    10: 'Десять', 11: 'Одиннадцать', 12: 'Двенадцать', 13: 'Тринадцать',
    14: 'Четырнадцать', 15: 'Пятнадцать', 16: 'Шестнадцать', 17: 'Семнадцать',
    18: 'Восемнадцать', 19: 'Девятнадцать', 20: 'Двадцать',
}

GROUP_COLOR = {
    'http': 'var(--g-http)',
    'data': 'var(--g-data)',
    'db': 'var(--g-db)',
    'view': 'var(--g-view)',
    'object': 'var(--g-object)',
}

ICON_CHEVRON = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3l5 5-5 5" fill="none" '
                'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_ARROW = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h9M8 4l4 4-4 4" fill="none" '
              'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" '
               'stroke="currentColor" stroke-width="2"/><path d="M16 16l4.5 4.5" stroke="currentColor" '
               'stroke-width="2" stroke-linecap="round"/></svg>')

NOTE_KIND = {'tip': 'совет', 'warn': 'внимание', 'trap': 'грабли'}


def esc(text):
    return html_mod.escape(str(text), quote=False)


def attr(text):
    return html_mod.escape(str(text), quote=True)


def inline(text):
    """Разметка внутри абзаца: `код`, **жирный**, [текст](адрес)."""
    parts = []
    for i, chunk in enumerate(re.split(r'(`[^`]+`)', text)):
        if i % 2:
            parts.append('<code>%s</code>' % esc(chunk[1:-1]))
            continue
        chunk = esc(chunk)
        chunk = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', chunk)
        chunk = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',
                       r'<a href="\2" target="_blank" rel="noopener">\1</a>', chunk)
        parts.append(chunk)
    return ''.join(parts)


# --------------------------------------------------------------------------- блоки

def block_code(lang, title, code):
    lang_label = site.LANG_LABELS.get(lang, lang.upper())
    head = '<div class="code-head">'
    if title:
        head += '<span class="cf">%s</span>' % esc(title)
    else:
        head += '<span class="cf"></span>'
    head += '<span class="cl">%s</span>' % esc(lang_label)
    head += '<button type="button" class="copy">копировать</button></div>'
    return '<figure class="code">%s<pre><code>%s</code></pre></figure>' % (
        head, site.highlight(code, lang))


def block_ref(items):
    rows = []
    for n, item in enumerate(items):
        search = (item['n'] + ' ' + item.get('d', '') + ' ' + item.get('o', '')).lower()
        body = ''
        if item.get('o'):
            body += '<p class="ref-o"><b>опции:</b> %s</p>' % inline(item['o'])
        if item.get('c'):
            body += '<figure class="code bare"><pre><code>%s</code></pre></figure>' % site.highlight(item['c'], 'php')
        rows.append(
            '<div class="ref-item" data-search="%s">'
            '<button type="button" class="ref-btn" aria-expanded="false">'
            '<span class="ref-n">%s</span>'
            '<span class="ref-d">%s</span>'
            '<span class="ref-chev">%s</span>'
            '</button>'
            '<div class="ref-body" hidden>%s</div>'
            '</div>' % (attr(search), esc(item['n']), inline(item.get('d', '')), ICON_CHEVRON, body))
    return (
        '<div class="ref-block">'
        '<div class="ref-tools">'
        '<label class="ref-search">%s<input type="text" placeholder="фильтр по названию и описанию" '
        'aria-label="Фильтр по списку"></label>'
        '<span class="ref-count">%d шт.</span>'
        '</div>'
        '<div class="ref">%s</div>'
        '<div class="ref-empty" hidden>Ничего не нашлось. Попробуйте другое слово.</div>'
        '</div>' % (ICON_SEARCH, len(items), ''.join(rows)))


def block_kv(pairs):
    rows = ''.join('<div class="kv-row"><div class="kv-k">%s</div><div class="kv-v">%s</div></div>'
                   % (esc(k), inline(v)) for k, v in pairs)
    return '<div class="kv">%s</div>' % rows


def block_note(kind, title, text):
    return ('<div class="note %s"><h4><span class="nk">%s</span>%s</h4><p>%s</p></div>'
            % (kind, esc(NOTE_KIND.get(kind, kind)), esc(title), inline(text)))


def block_svg(markup, caption):
    return ('<figure class="dgf"><div class="dg-wrap">%s</div>'
            '<figcaption>%s</figcaption></figure>' % (markup, inline(caption)))


def block_steps(items):
    return '<ol class="steps">%s</ol>' % ''.join('<li>%s</li>' % inline(i) for i in items)


DEMOS = {}


def demo(name):
    def wrap(fn):
        DEMOS[name] = fn
        return fn
    return wrap


@demo('validator-lab')
def demo_validator():
    return '''<div class="demo" data-demo="validator-lab">
  <div class="demo-head"><span class="dot"></span>проверьте прямо здесь</div>
  <div class="demo-body">
    <div class="row2">
      <div class="field"><label for="vl-kind">валидатор</label><select id="vl-kind"></select></div>
      <div class="field"><label for="vl-value">значение атрибута</label><input type="text" id="vl-value" value="Ян"></div>
    </div>
    <div class="row2" id="vl-opts"></div>
    <label class="check"><input type="checkbox" id="vl-skip" checked>
      <span>skipOnEmpty — пропускать пустое значение (так и есть по умолчанию)</span></label>
    <div class="verdict" id="vl-verdict"></div>
    <div><div class="out-label">эта же проверка в rules()</div><pre class="out" id="vl-rule"></pre></div>
  </div>
</div>'''


@demo('scenario-lab')
def demo_scenario():
    chips = ''.join(
        '<button type="button" class="chip" data-sc="%s" aria-pressed="%s">%s</button>'
        % (s, 'true' if s == 'default' else 'false', s)
        for s in ['default', 'register', 'profile', 'update', 'admin'])
    return '''<div class="demo" data-demo="scenario-lab">
  <div class="demo-head"><span class="dot"></span>переключите сценарий</div>
  <div class="demo-body">
    <div class="chips">%s</div>
    <div class="kv" id="sl-table"></div>
    <p class="lc-note" id="sl-hint"></p>
  </div>
</div>''' % chips


@demo('lifecycle-lab')
def demo_lifecycle():
    chips = ''.join(
        '<button type="button" class="chip" data-lc="%s" aria-pressed="%s">%s</button>'
        % (k, 'true' if k == 'insert' else 'false', label)
        for k, label in [('insert', 'save() — новая запись'), ('update', 'save() — изменение'),
                         ('delete', 'delete()'), ('find', 'find()')])
    return '''<div class="demo" data-demo="lifecycle-lab">
  <div class="demo-head"><span class="dot"></span>цепочка шаг за шагом</div>
  <div class="demo-body">
    <div class="chips">%s</div>
    <div class="lc" id="lc-list"></div>
    <p class="lc-note" id="lc-note"></p>
    <div class="btn-row"><button type="button" class="btn" id="lc-play">Выполнить</button></div>
  </div>
</div>''' % chips


@demo('query-lab')
def demo_query():
    items = [('status', 'where(status)'), ('like', 'andWhere(like)'), ('filter', 'andFilterWhere(пусто)'),
             ('in', 'andWhere(in)'), ('join', 'joinWith(author)'), ('joinwhere', 'where по author'),
             ('with', 'with(tags)'), ('group', 'groupBy'), ('order', 'orderBy'), ('limit', 'limit(10)')]
    chips = ''.join('<button type="button" class="chip" data-q="%s">%s</button>' % (k, esc(l))
                    for k, l in items)
    return '''<div class="demo" data-demo="query-lab">
  <div class="demo-head"><span class="dot"></span>соберите запрос кликами</div>
  <div class="demo-body">
    <div class="chips">%s</div>
    <div class="row2">
      <div><div class="out-label">Active Record</div><pre class="out" id="ql-php"></pre></div>
      <div><div class="out-label">итоговый SQL</div><pre class="out" id="ql-sql"></pre></div>
    </div>
    <p class="lc-note" id="ql-note" hidden></p>
  </div>
</div>''' % chips


def render_block(b):
    kind = b[0]
    if kind == 'p':
        return '<p>%s</p>' % inline(b[1])
    if kind == 'h':
        return '<h3>%s</h3>' % esc(b[1])
    if kind == 'code':
        return block_code(b[1], b[2], b[3])
    if kind == 'svg':
        return block_svg(b[1], b[2])
    if kind == 'ref':
        return block_ref(b[1])
    if kind == 'kv':
        return block_kv(b[1])
    if kind == 'steps':
        return block_steps(b[1])
    if kind == 'note':
        return block_note(b[1], b[2], b[3])
    if kind == 'demo':
        fn = DEMOS.get(b[1])
        if not fn:
            raise SystemExit('неизвестная демонстрация: %s' % b[1])
        return fn()
    raise SystemExit('неизвестный блок: %s' % kind)


# --------------------------------------------------------------------------- схема-карта

def node(x, y, w, h, num, name, topic=None, color=None, cls=''):
    """Узел карты: номер и подпись; цвет семейства подмешан в рамку и номер."""
    klass = 'mp-node' + (' mp-hit' if topic else '') + (' ' + cls if cls else '')
    attrs = ' style="--gc: %s"' % color if color else ''
    if topic:
        attrs += ' data-open="%s" role="link" tabindex="0"' % topic
    cx = x + w / 2.0
    out = '<g class="%s"%s>' % (klass, attrs)
    out += '<rect x="%g" y="%g" width="%g" height="%g" rx="8"/>' % (x, y, w, h)
    if num:
        out += '<text x="%g" y="%g" class="mp-num">%s</text>' % (cx, y + 19, num)
        out += '<text x="%g" y="%g">%s</text>' % (cx, y + 37, esc(name))
    else:
        out += '<text x="%g" y="%g">%s</text>' % (cx, y + h / 2.0 + 4, esc(name))
    out += '</g>'
    return out


def build_map():
    C = GROUP_COLOR
    n = data.NUM
    p = []
    p.append('<svg viewBox="0 0 1060 424" role="img" class="mp" '
             'aria-label="Устройство Yii 2: сверху путь запроса — браузер, маршруты, фильтры, действие, '
             'ответ; посередине механизмы, которые действие дёргает; снизу фундамент из компонентов, '
             'поведений, событий и хелперов">')
    p.append('<defs><marker id="mp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" class="mp-head"/></marker></defs>')

    # фундамент
    p.append('<rect class="mp-slab" x="16" y="268" width="1028" height="132" rx="12" stroke-dasharray="5 4"/>')
    p.append('<text class="mp-label" style="fill: %s" x="36" y="292">'
             'фундамент · на этом стоит всё остальное</text>' % C['object'])

    # путь запроса: x, ширина, подпись, тема, цвет семейства, класс
    path = [
        (16, 100, '', 'браузер', None, None, 'mp-io'),
        (150, 124, n['http'], 'запрос', 'http', C['http'], ''),
        (308, 132, n['routing'], 'маршруты', 'routing', C['http'], ''),
        (474, 124, n['filters'], 'фильтры', 'filters', C['http'], ''),
        (632, 132, '', 'действие', None, None, ''),
        (798, 112, n['http'], 'ответ', 'http', C['http'], ''),
        (944, 100, '', 'браузер', None, None, 'mp-io'),
    ]
    for x, w, num, name, tid, color, cls in path:
        p.append(node(x, 36, w, 50, num, name, tid, color, cls))

    p.append('<g class="mp-flow" marker-end="url(#mp-a)">')
    for a, b in zip(path, path[1:]):
        # стрелка не упирается в рамку: остаётся зазор, чтобы не наезжать на метку семейства
        gap_from = a[0] + a[1] + 4
        p.append('<path d="M%d 61h%d"/>' % (gap_from, b[0] - 6 - gap_from))
    p.append('</g>')

    # механизмы, которые дёргает действие
    mech = [
        (16, 96, 'model', 'модель'),
        (124, 100, 'rules', 'правила'),
        (236, 104, 'scenarios', 'сценарии'),
        (370, 120, 'ar', 'Active Record'),
        (502, 124, 'query', 'Query Builder'),
        (638, 100, 'migrations', 'миграции'),
        (768, 96, 'widgets', 'виджеты'),
        (876, 168, 'state', 'кэш · сессии · куки'),
    ]
    group_of = {t['id']: t['group'] for t in data.TOPICS}
    centers = [x + w / 2.0 for x, w, _, _ in mech]

    # шина от действия вниз и разводка по механизмам
    p.append('<g class="mp-flow">')
    p.append('<path d="M698 86v28"/>')
    p.append('<path d="M%g 114h%g"/>' % (centers[0], centers[-1] - centers[0]))
    for cx in centers:
        p.append('<path d="M%g 114v30"/>' % cx)
    p.append('</g>')

    for x, w, tid, name in mech:
        p.append(node(x, 144, w, 50, n[tid], name, tid, C[group_of[tid]]))

    for x, label, color in [(16, 'данные и правила', C['data']),
                            (370, 'база данных', C['db']),
                            (768, 'вывод и состояние', C['view'])]:
        p.append('<text class="mp-label" style="fill: %s" x="%d" y="218">%s</text>' % (color, x, label))

    # связи фундамента с механизмами
    p.append('<g class="mp-tie">')
    for x in (150, 360, 570, 780):
        p.append('<path d="M%d 268v-36"/>' % x)
    p.append('</g>')

    # фундамент: узлы
    for x, tid, name in [(60, 'components', 'компоненты'), (304, 'behaviors', 'поведения'),
                         (548, 'events', 'события'), (792, 'helpers', 'хелперы')]:
        p.append(node(x, 312, 220, 52, n[tid], name, tid, C['object']))

    p.append('</svg>')
    return ''.join(p)


# --------------------------------------------------------------------------- страница

def build_cards():
    out = []
    for gid, gtitle, gblurb in data.GROUPS:
        topics = [t for t in data.TOPICS if t['group'] == gid]
        if not topics:
            continue
        cards = []
        for t in topics:
            cards.append(
                '<button type="button" class="card" style="--gc: %s" data-open="%s">'
                '<span class="card-top"><span class="card-num">%s</span>'
                '<span class="card-badge">%s</span></span>'
                '<h3>%s</h3>'
                '<span class="card-cls">%s</span>'
                '<p>%s</p>'
                '<span class="card-open">разобрать %s</span>'
                '</button>' % (
                    GROUP_COLOR[gid], attr(t['id']), esc(t['num']), esc(t['badge']),
                    esc(t['title']), esc(t['cls']), esc(t['lead']), ICON_ARROW))
        out.append(
            '<section class="group" style="--gc: %s">'
            '<div class="group-head"><span class="group-rule"></span>'
            '<h2>%s</h2><p>%s</p></div>'
            '<div class="cards">%s</div>'
            '</section>' % (GROUP_COLOR[gid], esc(gtitle), esc(gblurb), ''.join(cards)))
    return ''.join(out)


def build_topics():
    out = []
    for t in data.TOPICS:
        tabs, panels = [], []
        for i, (tid, tlabel, blocks) in enumerate(t['tabs']):
            tabs.append('<button type="button" class="tab" role="tab" data-tab="%s" aria-selected="%s">%s</button>'
                        % (attr(tid), 'true' if i == 0 else 'false', esc(tlabel)))
            body = ''.join(render_block(b) for b in blocks)
            panels.append('<div class="tab-panel" role="tabpanel" data-tab="%s"%s>%s</div>'
                          % (attr(tid), '' if i == 0 else ' hidden', body))
        out.append(
            '<article class="topic" id="topic-%s" data-num="%s" data-title="%s" data-color="%s" hidden>'
            '<header class="panel-hero"><div class="pe">узел %s · %s</div>'
            '<h2>%s</h2><p class="panel-lead">%s</p></header>'
            '<div class="tabs" role="tablist">%s</div>%s'
            '</article>' % (
                attr(t['id']), attr(t['num']), attr(t['title']), GROUP_COLOR[t['group']],
                esc(t['num']), esc(t['cls']), esc(t['title']), esc(t['lead']),
                ''.join(tabs), ''.join(panels)))
    return ''.join(out)


def build_page():
    css = open(os.path.join(SRC, 'explorer.css'), encoding='utf-8').read()
    js = open(os.path.join(SRC, 'explorer.js'), encoding='utf-8').read()

    refs = sum(len(b[1]) for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'ref')
    demos = sum(1 for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'demo')

    head = '''<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600;700&family=Golos+Text:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
%s
</style>''' % (esc(TITLE), css)

    body = '''<header class="top">
  <div class="top-in">
    <span class="mark"><b>Yii</b>Разборный Yii 2</span>
    <span class="top-spacer"></span>
    <a class="back-link" href="index.html">к шпаргалке</a>
    <button type="button" class="icon-btn" id="theme-btn" aria-label="Переключить тему">
      <svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
      <svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
</header>

<main>
  <div class="wrap">
    <section class="hero">
      <p class="eyebrow">каталог механизмов · Yii 2.0</p>
      <h1>Фреймворк, <span>разобранный на узлы</span></h1>
      <p class="hero-lead">%s механизмов, из которых состоит почти любое приложение на Yii.
        Нажмите на узел: внутри схема работы, полный список всего встроенного, заготовка своего варианта
        и грабли, на которые наступают чаще всего.</p>
      <ul class="hero-stats">
        <li><b>%d</b><span>узлов</span></li>
        <li><b>%d</b><span>встроенных возможностей</span></li>
        <li><b>%d</b><span>живые демонстрации</span></li>
      </ul>
    </section>

    <section class="map">
      <figure>
        <div class="map-frame">%s</div>
        <figcaption>Запрос идёт по верхней линии: маршруты выбирают действие, фильтры решают,
          пускать ли к нему. Действие дёргает механизмы посередине — модель с правилами, базу,
          виджеты для вывода, хранилища состояния. Внизу — то, на чём держится всё остальное: любой
          из этих узлов настраивается массивом, слушает события и принимает поведения.
          Номера идут в том же порядке, в каком узлы встречаются на пути запроса, цвет обозначает
          семейство. Узлы кликабельны.</figcaption>
      </figure>
    </section>

    <div class="groups">%s</div>

    <footer class="foot">
      <p>Авторский конспект официального руководства Yii 2.0. Примеры переписаны и сокращены,
        полный текст руководства — на <a href="https://www.yiiframework.com/doc/guide/2.0/ru" target="_blank" rel="noopener">yiiframework.com</a>,
        описание всех классов — в <a href="https://www.yiiframework.com/doc/api/2.0" target="_blank" rel="noopener">справочнике API</a>.</p>
      <p>Esc закрывает панель. Адрес в строке браузера меняется, поэтому на любой узел можно дать ссылку.</p>
    </footer>
  </div>
</main>

<div class="scrim" id="scrim" hidden></div>
<div class="panel" id="panel" role="dialog" aria-modal="true" aria-label="Разбор узла" hidden>
  <div class="panel-bar">
    <span class="pb-num" id="pb-num"></span>
    <span class="pb-title" id="pb-title"></span>
    <span class="sp"></span>
    <kbd>Esc</kbd>
    <button type="button" class="icon-btn" id="panel-close" aria-label="Закрыть">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
  <div class="panel-body"><div class="panel-body-in" id="panel-body-in"></div></div>
</div>

<div id="topic-store" hidden>%s</div>

<script>
%s
</script>''' % (NUMERALS.get(len(data.TOPICS), str(len(data.TOPICS))), len(data.TOPICS),
                refs, demos, build_map(), build_cards(), build_topics(), js)

    return head, body


def main():
    head, body = build_page()
    fragment = head + '\n\n' + body + '\n'

    standalone = ('<!doctype html>\n<html lang="ru">\n<head>\n'
                  '<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                  '<meta name="description" content="%s">\n'
                  '<meta name="color-scheme" content="light dark">\n'
                  '%s\n</head>\n<body>\n%s\n</body>\n</html>\n'
                  % (attr(DESCRIPTION), head, body))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(standalone)
    with open(FRAGMENT, 'w', encoding='utf-8') as fh:
        fh.write(fragment)

    print('Узлов: %d, справочных записей: %d, демонстраций: %d'
          % (len(data.TOPICS),
             sum(len(b[1]) for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'ref'),
             sum(1 for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'demo')))
    print('Готово: %s (%.0f КБ)' % (OUT, os.path.getsize(OUT) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
