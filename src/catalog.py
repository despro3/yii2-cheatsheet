# -*- coding: utf-8 -*-
"""Общий движок страниц-справочников: разметка блоков, узлы карты, каркас страницы.

Справочники по Yii 2 (build_explorer.py) и по PHP 8+ (build_php.py) устроены
одинаково: схема-карта наверху, у каждого её узла — панель с вкладками, внутри
вкладок — блоки. Всё, что у страниц общее, лежит здесь; своё у каждой — тексты,
сама схема и живые демонстрации.

Блок — кортеж, первый элемент задаёт тип:
  ('p', текст)                         абзац; поддерживает `код`, **жирный**, [ссылка](url)
  ('h', текст)                         подзаголовок внутри вкладки
  ('code', lang, title|None, код)      блок кода с подсветкой
  ('svg', разметка, подпись)           схема
  ('ref', [ {n, d, o, c, v, lang} ])   перечень встроенного с фильтром
  ('kv', [(ключ, значение)])           таблица «ключ — значение»
  ('steps', [шаг, ...])                нумерованная последовательность
  ('note', kind, заголовок, текст)     врезка: tip | warn | trap
  ('demo', id)                         интерактивная вставка
"""

import html as html_mod
import os
import re

import build as site                    # подсветка кода берём из основной сборки

ICON_TICK = ('<svg class="tick" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.5l3 3 6-6" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
             'stroke-linejoin="round"/></svg>')
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


# сквозная нумерация списков: панели примера нужен собственный id для aria-controls
REF_SEQ = [0]


def block_ref(items):
    """Список встроенного + панель примера.

    Раскрывающийся список заставлял открывать пункты по одному и уезжал вниз
    на каждом клике. Здесь выбранный пункт показывается рядом, так что 24
    валидатора можно просмотреть, не теряя места в списке.
    """
    REF_SEQ[0] += 1
    pane_id = 'rp-%d' % REF_SEQ[0]
    rows = []
    head = ('', '')
    lead = ''
    for n, item in enumerate(items):
        search = (item['n'] + ' ' + item.get('d', '') + ' ' + item.get('o', '')).lower()
        # метка версии: пункт появился в PHP такой-то; у справочника по Yii её нет
        ver = ''
        if item.get('v'):
            ver = '<i class="ref-v">%s</i>' % esc(item['v'])
            search += ' php ' + item['v'].lower()
        body = ''
        if item.get('o'):
            body += '<p class="ref-o"><b>опции:</b> %s</p>' % inline(item['o'])
        if item.get('c'):
            # примеры в списке почти всегда на PHP, но бывают строки ini и json
            body += ('<figure class="code bare"><pre><code>%s</code></pre></figure>'
                     % site.highlight(item['c'], item.get('lang', 'php')))
        if n == 0:
            # первый пункт разложен в панель прямо при сборке: до загрузки
            # скрипта страница уже показывает пример, а не пустое место
            head = (esc(item['n']) + ver, inline(item.get('d', '')))
            lead = body
        rows.append(
            '<div class="ref-item%s" data-search="%s">'
            '<button type="button" class="ref-btn" aria-controls="%s"%s>'
            '<span class="ref-n">%s%s</span>'
            '<span class="ref-d">%s</span>'
            '</button>'
            '<div class="ref-body" hidden>%s</div>'
            '</div>' % (' is-active' if n == 0 else '', attr(search), pane_id,
                        ' aria-current="true"' if n == 0 else '',
                        esc(item['n']), ver, inline(item.get('d', '')), body))
    return (
        '<div class="ref-block">'
        '<div class="ref-tools">'
        '<label class="ref-search">%s<input type="text" placeholder="фильтр по названию и описанию" '
        'aria-label="Фильтр по списку"></label>'
        '<span class="ref-count">%d шт.</span>'
        '</div>'
        '<div class="ref-work">'
        '<div class="ref">%s</div>'
        '<div class="ref-pane" id="%s" role="region" aria-label="Пример выбранного пункта">'
        '<p class="rp-kicker">пример</p>'
        '<h4 class="rp-name">%s</h4>'
        '<p class="rp-desc">%s</p>'
        '<div class="rp-body">%s</div>'
        '</div>'
        '</div>'
        '<div class="ref-empty" hidden>Ничего не нашлось. Попробуйте другое слово.</div>'
        '</div>' % (ICON_SEARCH, len(items), ''.join(rows), pane_id, head[0], head[1], lead))


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



def make_render(demos):
    """Отдаёт функцию отрисовки блока: у каждой страницы свой набор демонстраций."""

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
            fn = demos.get(b[1])
            if not fn:
                raise SystemExit('неизвестная демонстрация: %s' % b[1])
            return fn()
        raise SystemExit('неизвестный блок: %s' % kind)

    return render_block


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



def build_index(groups, topics, colors):
    """Указатель для узкого экрана: карта там уезжает в прокрутку."""
    out = []
    for gid, gtitle, _ in groups:
        items = ''.join(
            '<li><button type="button" data-open="%s">%s<b>%s</b><span>%s</span></button></li>'
            % (attr(t['id']), ICON_TICK, esc(t['title']), esc(t['badge']))
            for t in topics if t['group'] == gid)
        out.append('<section class="ix-group" style="--gc: %s"><h2>%s</h2><ul>%s</ul></section>'
                   % (colors[gid], esc(gtitle), items))
    return '<nav class="index" aria-label="Все узлы списком">%s</nav>' % ''.join(out)


def build_topics(topics, colors, render_block):
    REF_SEQ[0] = 0
    out = []
    for t in topics:
        tabs, panels = [], []
        for i, (tid, tlabel, blocks) in enumerate(t['tabs']):
            tabs.append('<button type="button" class="tab" role="tab" data-tab="%s" aria-selected="%s">%s</button>'
                        % (attr(tid), 'true' if i == 0 else 'false', esc(tlabel)))
            body = ''.join(render_block(b) for b in blocks)
            panels.append('<div class="tab-panel" role="tabpanel" data-tab="%s"%s>%s</div>'
                          % (attr(tid), '' if i == 0 else ' hidden', body))
        out.append(
            '<article class="topic" id="topic-%s" data-title="%s" data-color="%s" hidden>'
            '<header class="panel-hero"><div class="pe">%s</div>'
            '<h2>%s</h2><p class="panel-lead">%s</p></header>'
            '<div class="tabs" role="tablist">%s</div>%s'
            '</article>' % (
                attr(t['id']), attr(t['title']), colors[t['group']],
                esc(t['cls']), esc(t['title']), esc(t['lead']),
                ''.join(tabs), ''.join(panels)))
    return ''.join(out)


def write_page(out_path, fragment_path, title, description, head, body):
    """Пишет самостоятельную страницу и тот же текст без обвязки — для публикации."""
    fragment = head + '\n\n' + body + '\n'
    standalone = ('<!doctype html>\n<html lang="ru">\n<head>\n'
                  '<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                  '<meta name="description" content="%s">\n'
                  '<meta name="color-scheme" content="light dark">\n'
                  '%s\n</head>\n<body>\n%s\n</body>\n</html>\n'
                  % (attr(description), head, body))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(standalone)
    with open(fragment_path, 'w', encoding='utf-8') as fh:
        fh.write(fragment)
    return os.path.getsize(out_path)
