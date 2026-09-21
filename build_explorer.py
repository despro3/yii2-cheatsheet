# -*- coding: utf-8 -*-
"""Сборка страницы «Справочник Yii 2» из src/explorer/.

    python3 build_explorer.py

Пишет два файла:
    docs/explorer.html            самостоятельная страница (открывается из файла)
    src/explorer/_fragment.html   та же страница без обвязки, для публикации
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'explorer')
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, ROOT)

import catalog                            # noqa: E402  общий движок справочников
import content as data                    # noqa: E402
from catalog import attr, esc, node       # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'explorer.html')
FRAGMENT = os.path.join(SRC, '_fragment.html')

TITLE = 'Справочник Yii 2'
DESCRIPTION = ('Каталог механизмов Yii 2: карточки основных узлов фреймворка, '
               'полные списки встроенного и живые демонстрации.')
GROUP_COLOR = {
    'http': 'var(--g-http)',
    'data': 'var(--g-data)',
    'db': 'var(--g-db)',
    'view': 'var(--g-view)',
    'object': 'var(--g-object)',
}

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



# отрисовка блока знает про демонстрации этой страницы
render_block = catalog.make_render(DEMOS)

# --------------------------------------------------------------------------- схема-карта

def node(x, y, w, h, label, sub, topic=None, color=None, cls='', tip=None):
    """Блок карты: подпись, при наличии — вторая строка, и данные для подсказки."""
    klass = 'mp-node' + (' mp-hit' if topic else '') + (' ' + cls if cls else '')
    attrs = ' style="--gc: %s"' % color if color else ''
    if topic:
        attrs += ' data-open="%s" role="link" tabindex="0"' % topic
    if tip:
        attrs += (' data-tip-title="%s" data-tip-cls="%s" data-tip-badge="%s" data-tip-lead="%s"'
                  % (attr(tip['title']), attr(tip['cls']), attr(tip['badge']), attr(tip['lead'])))
    cx = x + w / 2.0
    out = '<g class="%s"%s>' % (klass, attrs)
    out += '<rect x="%g" y="%g" width="%g" height="%g" rx="8"/>' % (x, y, w, h)
    if topic:
        # отметка «изучено»: показывается стилями, когда на группе есть класс is-done
        tx, ty = x + w - 13, y + 12
        out += ('<path class="mp-tick" d="M%g %gL%g %gL%g %g"/>'
                % (tx - 3.4, ty, tx - 1, ty + 2.6, tx + 3.6, ty - 2.8))
    if sub:
        out += '<text x="%g" y="%g">%s</text>' % (cx, y + h * 0.40, esc(label))
        out += '<text x="%g" y="%g" class="mp-sub">%s</text>' % (cx, y + h * 0.72, esc(sub))
    else:
        out += '<text x="%g" y="%g">%s</text>' % (cx, y + h / 2.0 + 4, esc(label))
    out += '</g>'
    return out


# петля ответа: подпись стоит на линии, поэтому линия разорвана вокруг неё
RET_X, RET_GAP = 553, 28


def build_map():
    C = GROUP_COLOR
    by_id = {t['id']: t for t in data.TOPICS}

    def tip(tid):
        t = by_id[tid]
        return {'title': t['title'], 'cls': t['cls'], 'badge': t['badge'], 'lead': t['lead']}

    p = []
    p.append('<svg viewBox="0 0 1060 592" role="img" class="mp" '
             'aria-label="Устройство Yii 2: сверху путь запроса от браузера через приложение, маршрут, '
             'контроллер и фильтры к действию, откуда ответ возвращается в браузер; ниже три семейства '
             'механизмов, которые действие '
             'дёргает; внизу фундамент, на котором стоит всё остальное">')
    p.append('<defs><marker id="mp-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" class="mp-head"/></marker></defs>')

    # фундамент
    p.append('<rect class="mp-slab" x="40" y="436" width="980" height="140" rx="12" stroke-dasharray="5 4"/>')
    p.append('<text class="mp-label" style="fill: %s" x="530" y="462" text-anchor="middle">'
             'фундамент · на этом стоит всё остальное</text>' % C['object'])

    # путь запроса: порядок ровно такой, в каком его проходит запрос
    path = [
        (28, 92, 'браузер', None, None, 'mp-io'),
        (162, 96, 'запрос', 'http', C['http'], ''),
        (300, 124, 'приложение', 'app', C['http'], ''),
        (466, 104, 'маршрут', 'routing', C['http'], ''),
        (612, 124, 'контроллер', 'controllers', C['http'], ''),
        (778, 104, 'фильтры', 'filters', C['http'], ''),
        (924, 108, 'действие', None, None, ''),
    ]
    for x, w, label, tid, color, cls in path:
        p.append(node(x, 34, w, 52, label, None, tid, color, cls, tip(tid) if tid else None))

    p.append('<g class="mp-flow" marker-end="url(#mp-a)">')
    for a, b in zip(path, path[1:]):
        gap_from = a[0] + a[1] + 5
        p.append('<path d="M%d 60h%d"/>' % (gap_from, b[0] - 7 - gap_from))
    # ответ — это сама петля возврата: отдельным блоком он был бы вторым входом в ту же панель.
    # спуск к «браузеру» длиннее наконечника, иначе тот начинается раньше поворота и висит без хвоста
    p.append('<path d="M%g 14H74v18"/>' % (RET_X - RET_GAP,))
    # доступ не отдельная стадия: его спрашивают фильтры
    p.append('<path d="M830 86v14"/>')
    p.append('</g>')
    # длинная часть петли идёт без наконечника и разорвана под подписью
    p.append('<g class="mp-flow"><path d="M1032 60H1044V14H%g"/></g>' % (RET_X + RET_GAP,))
    p.append('<text class="mp-label" style="fill: %s" x="%g" y="18" text-anchor="middle">ответ</text>'
             % (C['http'], RET_X))
    p.append(node(774, 104, 112, 46, 'доступ', None, 'user', C['http'], '', tip('user')))

    # механизмы: колонка на семейство
    columns = [
        ('данные и правила', C['data'], ['model', 'rules', 'scenarios'],
         ['модель', 'правила', 'сценарии']),
        ('база данных', C['db'], ['ar', 'query', 'migrations'],
         ['Active Record', 'Query Builder', 'миграции']),
        ('вывод и состояние', C['view'], ['views', 'widgets', 'state'],
         ['представления', 'виджеты', 'кэш · сессии · куки']),
    ]
    cx0, cw, cstep = 66, 210, 359
    centers = [cx0 + i * cstep + cw / 2.0 for i in range(len(columns))]

    # шина: действие тянется к каждому семейству
    p.append('<g class="mp-flow">')
    p.append('<path d="M978 86v78"/>')
    p.append('<path d="M%g 164H978"/>' % centers[0])
    p.append('</g>')
    p.append('<g class="mp-flow" marker-end="url(#mp-a)">')
    for c in centers:
        p.append('<path d="M%g 164v12"/>' % c)
    p.append('</g>')

    for i, (label, color, ids, labels) in enumerate(columns):
        p.append('<text class="mp-label" style="fill: %s" x="%g" y="194" text-anchor="middle">%s</text>'
                 % (color, centers[i], label))
        for row, (tid, name) in enumerate(zip(ids, labels)):
            p.append(node(cx0 + i * cstep, 206 + row * 72, cw, 60,
                          name, by_id[tid]['badge'], tid, color, '', tip(tid)))

    # фундамент: узлы
    base = [('components', 'компоненты'), ('di', 'DI-контейнер'), ('behaviors', 'поведения'),
            ('events', 'события'), ('helpers', 'хелперы')]
    for i, (tid, name) in enumerate(base):
        p.append(node(66 + i * 188, 482, 176, 60, name, by_id[tid]['badge'], tid, C['object'], '', tip(tid)))

    p.append('</svg>')
    return ''.join(p)

def build_page():
    css = open(os.path.join(SRC, 'explorer.css'), encoding='utf-8').read()
    js = open(os.path.join(SRC, 'explorer.js'), encoding='utf-8').read()

    refs = sum(len(b[1]) for t in data.TOPICS for _, _, bl in t['tabs'] for b in bl if b[0] == 'ref')

    # быстрый режим открывает вкладку со списком встроенного; проверяем, что она у всех одна и та же
    quick_tabs = {t['tabs'][1][0] for t in data.TOPICS if len(t['tabs']) > 1}
    assert len(quick_tabs) == 1, 'вторая вкладка называется по-разному: %s' % sorted(quick_tabs)
    quick_tab = quick_tabs.pop()
    assert all(any(b[0] == 'ref' for b in t['tabs'][1][2]) for t in data.TOPICS), \
        'на второй вкладке не у всех узлов есть список'

    head = '''<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
%s
</style>''' % (esc(TITLE), css)

    body = '''<header class="top">
  <div class="top-in">
    <span class="mark"><b>Yii</b><span class="mark-text">Справочник Yii 2</span></span>
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
        <figcaption>Запрос идёт по верхней линии; ниже — механизмы, которые дёргает действие,
          а внизу то, на чём держится всё остальное. Нажмите на блок, чтобы открыть разбор;
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
%s
</script>''' % (len(data.TOPICS), refs, len(data.TOPICS), quick_tab,
                build_map(), catalog.build_index(data.GROUPS, data.TOPICS, GROUP_COLOR),
                catalog.build_topics(data.TOPICS, GROUP_COLOR, render_block), js)

    return head, body

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
