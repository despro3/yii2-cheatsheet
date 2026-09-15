#!/usr/bin/env python3
"""Собирает шпаргалку Yii2 из content/*.md в самодостаточный index.html.

Запуск:  python3 build.py
"""

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, 'content')
SITE = os.path.join(ROOT, 'site')
OUT = os.path.join(ROOT, 'index.html')

LANG_MAP = {
    'php': 'php', 'bash': 'bash', 'sh': 'bash', 'shell': 'bash', 'console': 'bash',
    'json': 'json', 'sql': 'sql', 'nginx': 'nginx', 'apacheconf': 'apache',
    'html': 'xml', 'xml': 'xml', 'js': 'javascript', 'javascript': 'javascript',
    'css': 'css', 'ini': 'ini', 'yaml': 'yaml', 'yml': 'yaml', 'diff': 'diff',
    'text': 'plaintext', '': 'plaintext',
}
LANG_LABEL = {
    'php': 'php', 'bash': 'shell', 'json': 'json', 'sql': 'sql', 'nginx': 'nginx',
    'apache': 'apache', 'xml': 'html', 'javascript': 'js', 'css': 'css',
    'ini': 'ini', 'yaml': 'yaml', 'diff': 'diff', 'plaintext': 'text',
}

TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya', 'і': 'i', 'ї': 'i', 'є': 'e', 'ґ': 'g',
}


def slugify(text, used):
    text = re.sub(r'`([^`]*)`', r'\1', text).lower()
    out = []
    for ch in text:
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isalnum() and ord(ch) < 128:
            out.append(ch)
        else:
            out.append('-')
    slug = re.sub(r'-{2,}', '-', ''.join(out)).strip('-') or 'section'
    slug = slug[:48].strip('-')
    base, n = slug, 2
    while slug in used:
        slug = '%s-%d' % (base, n)
        n += 1
    used.add(slug)
    return slug


# ---------------------------------------------------------------- inline

CODE_TOKEN = '\x00CODE%d\x00'


def inline(text):
    """Инлайновая разметка: `код`, **жирный**, *курсив*, [ссылки](url), <autolink>."""
    spans = []

    def stash(m):
        spans.append(html.escape(m.group(1), quote=False))
        return CODE_TOKEN % (len(spans) - 1)

    text = re.sub(r'`([^`]+)`', stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r'&lt;(https?://[^\s&]+)&gt;',
                  lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (m.group(1), m.group(1)),
                  text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
                  lambda m: '<a href="%s"%s>%s</a>' % (
                      m.group(2),
                      ' target="_blank" rel="noopener"' if m.group(2).startswith('http') else '',
                      m.group(1)),
                  text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', text)

    for i, span in enumerate(spans):
        text = text.replace(CODE_TOKEN % i, '<code>%s</code>' % span)
    return text


def plain(text):
    """Текст без разметки — для поискового индекса."""
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = text.replace('**', '').replace('|', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def split_row(row):
    """Делит строку таблицы по |, игнорируя разделители внутри `кода`."""
    cells, buf, in_code = [], '', False
    for ch in row.strip().strip('|'):
        if ch == '`':
            in_code = not in_code
            buf += ch
        elif ch == '|' and not in_code:
            cells.append(buf.strip())
            buf = ''
        else:
            buf += ch
    cells.append(buf.strip())
    return cells


# ---------------------------------------------------------------- block parser

def parse(md, section_id, used_slugs):
    """Возвращает (html, headings, index_entries)."""
    lines = md.split('\n')
    out, headings, entries = [], [], []
    i, n = 0, len(lines)

    current = {'anchor': section_id, 'title': None, 'depth': 1, 'text': []}

    def flush_entry():
        if current['title'] is None:
            return
        text = plain(' '.join(current['text']))[:900]
        entries.append({
            's': None, 'a': current['anchor'], 't': current['title'],
            'd': current['depth'], 'x': text,
        })

    def collect(raw):
        if len(current['text']) < 60:
            current['text'].append(raw)

    while i < n:
        line = lines[i]

        # заголовки
        m = re.match(r'^(#{1,4})\s+(.*)$', line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            if level == 1:
                i += 1
                continue  # H1 выводится в шапке раздела
            flush_entry()
            slug = slugify(title, used_slugs)
            tag = 'h2' if level == 2 else 'h3'
            headings.append({'level': min(level, 3), 'id': slug, 'title': plain(title)})
            out.append(
                '<%s id="%s" data-title="%s">%s<a class="anchor" href="#%s" aria-label="Ссылка на раздел">#</a></%s>'
                % (tag, slug, html.escape(plain(title), quote=True), inline(title), slug, tag))
            current = {'anchor': slug, 'title': plain(title), 'depth': min(level, 3), 'text': []}
            i += 1
            continue

        # код
        m = re.match(r'^```([\w+-]*)\s*$', line)
        if m:
            lang = LANG_MAP.get(m.group(1).lower(), 'plaintext')
            i += 1
            buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            code = '\n'.join(buf)
            collect(code)
            out.append(
                '<div class="code"><div class="code-bar"><span class="code-lang">%s</span>'
                '<button type="button" class="copy" aria-label="Скопировать код">'
                '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.8">'
                '<rect x="9" y="9" width="11" height="11" rx="2"/>'
                '<path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg><span>копировать</span></button></div>'
                '<pre><code data-lang="%s">%s</code></pre></div>'
                % (LANG_LABEL.get(lang, lang), lang, html.escape(code, quote=False)))
            continue

        # таблица
        if line.startswith('|') and i + 1 < n and re.match(r'^\|[\s:|-]+\|?\s*$', lines[i + 1]):
            head = split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].startswith('|'):
                rows.append(split_row(lines[i]))
                i += 1
            collect(' '.join(head) + ' ' + ' '.join(' '.join(r) for r in rows))
            thead = ''.join('<th>%s</th>' % inline(c) for c in head)
            tbody = ''.join(
                '<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in rows)
            out.append('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % (thead, tbody))
            continue

        # цитата / врезка
        if line.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            text = ' '.join(x.strip() for x in buf).strip()
            collect(text)
            kind, label = '', 'заметка'
            m2 = re.match(r'^(Важно|Внимание|Совет|Note|Tip|Warning)\s*:\s*(.*)$', text, re.I)
            if m2:
                word = m2.group(1).lower()
                text = m2.group(2)
                if word in ('важно', 'внимание', 'warning'):
                    kind, label = ' is-warn', 'важно'
                else:
                    kind, label = ' is-tip', 'совет'
            out.append('<div class="note%s"><span class="note-label">%s</span>'
                       '<div class="note-body"><p>%s</p></div></div>' % (kind, label, inline(text)))
            continue

        # списки
        if re.match(r'^\s*([-*]|\d+\.)\s+', line):
            block, base_indent = [], len(line) - len(line.lstrip())
            while i < n and (re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]) or
                             (lines[i].strip() and lines[i].startswith(' ' * (base_indent + 2)))):
                block.append(lines[i])
                i += 1
            collect(' '.join(block))
            out.append(render_list(block, base_indent))
            continue

        if re.match(r'^-{3,}\s*$', line):
            out.append('<hr>')
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        # параграф
        buf = []
        while i < n and lines[i].strip() and not re.match(
                r'^(#{1,4}\s|```|\||>|\s*([-*]|\d+\.)\s|-{3,}\s*$)', lines[i]):
            buf.append(lines[i].strip())
            i += 1
        text = ' '.join(buf)
        collect(text)
        out.append('<p>%s</p>' % inline(text))

    flush_entry()
    return '\n'.join(out), headings, entries


def render_list(block, base_indent):
    """Рекурсивно собирает ul/ol с вложенностью по отступам."""
    ordered = bool(re.match(r'^\s*\d+\.\s+', block[0]))
    items, current_item, child = [], None, []
    for raw in block:
        indent = len(raw) - len(raw.lstrip())
        m = re.match(r'^\s*([-*]|\d+\.)\s+(.*)$', raw)
        if m and indent <= base_indent:
            if current_item is not None:
                items.append((current_item, child))
            current_item, child = m.group(2), []
        else:
            child.append(raw)
    if current_item is not None:
        items.append((current_item, child))

    html_items = []
    for text, kids in items:
        inner = inline(text)
        if kids:
            nested = [k for k in kids if k.strip()]
            if nested and re.match(r'^\s*([-*]|\d+\.)\s+', nested[0]):
                nested_indent = len(nested[0]) - len(nested[0].lstrip())
                inner += render_list(nested, nested_indent)
            else:
                inner += ' ' + inline(' '.join(k.strip() for k in nested))
        html_items.append('<li>%s</li>' % inner)
    tag = 'ol' if ordered else 'ul'
    return '<%s>%s</%s>' % (tag, ''.join(html_items), tag)


# ---------------------------------------------------------------- сборка

def read_front_matter(text):
    meta = {}
    if text.startswith('---'):
        end = text.find('\n---', 3)
        block = text[3:end]
        text = text[end + 4:].lstrip('\n')
        for line in block.strip().split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
    return meta, text


def main():
    files = sorted(f for f in os.listdir(CONTENT) if f.endswith('.md'))
    if not files:
        sys.exit('content/*.md не найдены')

    sections, bodies, index = [], [], []
    used_slugs = set()

    for pos, name in enumerate(files):
        with open(os.path.join(CONTENT, name), encoding='utf-8') as fh:
            meta, md = read_front_matter(fh.read())
        sec_id = meta.get('id') or slugify(name, set())
        title = meta.get('title', sec_id)
        summary = meta.get('summary', '')
        num = '%02d' % (pos + 1)
        used_slugs.add(sec_id)

        body, headings, entries = parse(md, sec_id, used_slugs)
        h1 = re.search(r'^#\s+(.*)$', md, re.M)
        heading_text = h1.group(1).strip() if h1 else title

        sections.append({'id': sec_id, 'num': num, 'title': title, 'summary': summary})
        index.append({'s': pos, 'a': sec_id, 't': title, 'd': 1,
                      'x': plain(summary + ' ' + heading_text)})
        for entry in entries:
            entry['s'] = pos
            index.append(entry)
        bodies.append({'id': sec_id, 'num': num, 'title': title, 'summary': summary,
                       'heading': heading_text, 'body': body})

    # навигация
    nav = []
    for pos, sec in enumerate(sections):
        nav.append('<button type="button" class="nav-item" data-id="%s"><i>%s</i><span>%s</span></button>'
                   % (sec['id'], sec['num'], html.escape(sec['title'], quote=False)))

    # разделы
    rendered = []
    for pos, sec in enumerate(bodies):
        pager = []
        if pos > 0:
            prev = bodies[pos - 1]
            pager.append('<a class="pager-card" href="#%s"><span>← %s</span><b>%s</b></a>'
                         % (prev['id'], prev['num'], html.escape(prev['title'], quote=False)))
        if pos < len(bodies) - 1:
            nxt = bodies[pos + 1]
            pager.append('<a class="pager-card to-next" href="#%s"><span>%s →</span><b>%s</b></a>'
                         % (nxt['id'], nxt['num'], html.escape(nxt['title'], quote=False)))
        rendered.append(
            '<section id="%s" data-sec="%s"%s>\n'
            '<header class="sec-head"><div class="eyebrow"><span>раздел %s</span></div>'
            '<h1>%s</h1>%s</header>\n%s\n<nav class="pager">%s</nav>\n</section>'
            % (sec['id'], sec['id'], '' if pos == 0 else ' hidden', sec['num'],
               inline(sec['heading']),
               ('<p class="sec-summary">%s</p>' % inline(sec['summary'])) if sec['summary'] else '',
               sec['body'], ''.join(pager)))

    with open(os.path.join(SITE, 'styles.css'), encoding='utf-8') as fh:
        styles = fh.read()
    with open(os.path.join(SITE, 'app.js'), encoding='utf-8') as fh:
        app = fh.read()
    with open(os.path.join(SITE, 'shell.html'), encoding='utf-8') as fh:
        shell = fh.read()

    data = 'window.YII_SECTIONS=%s;\nwindow.YII_INDEX=%s;' % (
        json.dumps(sections, ensure_ascii=False, separators=(',', ':')),
        json.dumps(index, ensure_ascii=False, separators=(',', ':')))
    data = data.replace('</', '<\\/')

    page = (shell
            .replace('/*{{STYLES}}*/', styles)
            .replace('<!--{{NAV}}-->', '\n'.join(nav))
            .replace('<!--{{SECTIONS}}-->', '\n'.join(rendered))
            .replace('/*{{DATA}}*/', data)
            .replace('/*{{APP}}*/', app))

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(page)

    print('index.html: %.1f КБ, разделов: %d, записей в индексе: %d'
          % (len(page.encode('utf-8')) / 1024, len(sections), len(index)))


if __name__ == '__main__':
    main()
