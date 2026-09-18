#!/usr/bin/env python3
"""
Сборка сайта «Yii 2 — шпаргалка»: src/ → docs/

    python3 build.py           # собрать сайт
    python3 build.py --check   # только проверить покрытие глав и ссылки

Зависимостей нет — достаточно Python 3.8+.

Структура исходников:
    src/content/NN-id.md   разделы (Markdown + front matter)
    src/parts.json         части (группы) сайта в нужном порядке
    src/guide-chapters.json карта глав официального руководства
    src/templates/*.html   каркасы страниц
    src/assets/*           стили, скрипты, иконки (копируются как есть)
    src/diagrams/*.svg     диаграммы, подключаемые через :::diagram
"""

import html
import json
import os
import re
import hashlib
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
CONTENT = os.path.join(SRC, 'content')
TEMPLATES = os.path.join(SRC, 'templates')
ASSETS = os.path.join(SRC, 'assets')
DIAGRAMS = os.path.join(SRC, 'diagrams')
ARCHIVE = os.path.join(SRC, 'archive')
OUT = os.path.join(ROOT, 'docs')

GUIDE_URL = 'https://www.yiiframework.com/doc/guide/2.0/ru/%s'
API_URL = 'https://www.yiiframework.com/doc/api/2.0/%s'
SITE_NAME = 'Yii 2 — шпаргалка'


# --------------------------------------------------------------------------- utils

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def esc(text):
    return html.escape(text, quote=False)


def attr(text):
    return html.escape(text, quote=True)


TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
}


def slugify(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'`([^`]*)`', r'\1', text).lower()
    out = []
    for ch in text:
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
        else:
            out.append('-')
    slug = re.sub(r'-{2,}', '-', ''.join(out)).strip('-')
    return slug[:60].strip('-') or 'section'


def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s)


# --------------------------------------------------------------------------- highlighter

PHP_KEYWORDS = (
    'abstract and array as break callable case catch class clone const continue declare '
    'default do echo else elseif empty enddeclare endfor endforeach endif endswitch endwhile '
    'enum extends final finally fn for foreach function global goto if implements include '
    'include_once instanceof insteadof interface isset list match namespace new or print '
    'private protected public readonly require require_once return static switch throw trait '
    'try unset use var while xor yield'
).split()

JS_KEYWORDS = (
    'async await break case catch class const continue debugger default delete do else export '
    'extends finally for function if import in instanceof let new of return static super switch '
    'this throw try typeof var void while with yield'
).split()

SQL_KEYWORDS = (
    'select from where and or not in is null as insert into values update set delete create '
    'table drop alter add column primary key foreign references index unique default engine '
    'charset order by group having limit offset join inner left right outer on union all '
    'distinct count sum avg max min like between exists case when then else end begin commit '
    'rollback transaction truncate if int integer varchar char text blob datetime timestamp '
    'bigint tinyint smallint boolean float double decimal date time auto_increment'
).split()


def _alt(words):
    return r'\b(?:' + '|'.join(re.escape(w) for w in words) + r')\b'


STR = r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\""

LANG_RULES = {
    'php': [
        ('cm', r'/\*[\s\S]*?\*/|//[^\n]*|#(?!\[)[^\n]*'),
        ('at', r'#\[[^\]\n]*\]'),
        ('st', r"<<<'?(?P<hd>\w+)'?\n[\s\S]*?\n\s*(?P=hd)|" + STR),
        ('tg', r'<\?php|<\?=|\?>'),
        ('va', r'\$[A-Za-z_]\w*'),
        ('kw', _alt(PHP_KEYWORDS)),
        ('lt', r'\b(?:true|false|null|TRUE|FALSE|NULL|self|parent)\b'),
        ('nu', r'\b0x[0-9a-fA-F]+\b|\b\d[\d_]*(?:\.\d+)?\b'),
        ('ct', r'\b[A-Z][A-Z0-9_]{2,}\b'),
        ('cl', r'\\?[A-Za-z_]\w*(?:\\[A-Za-z_]\w*)+|\b[A-Z][A-Za-z0-9_]*\b'),
        ('fn', r'\b[a-z_]\w*(?=\s*\()'),
    ],
    'js': [
        ('cm', r'/\*[\s\S]*?\*/|//[^\n]*'),
        ('st', STR + r'|`(?:[^`\\]|\\.)*`'),
        ('kw', _alt(JS_KEYWORDS)),
        ('lt', r'\b(?:true|false|null|undefined|NaN)\b'),
        ('nu', r'\b\d[\d_]*(?:\.\d+)?\b'),
        ('cl', r'\b[A-Z][A-Za-z0-9_]*\b'),
        ('fn', r'\b[a-z_$]\w*(?=\s*\()'),
        ('va', r'\$'),
    ],
    'bash': [
        ('cm', r'(?m)(?<![\w$])#[^\n]*'),
        ('st', STR),
        ('va', r'\$\{?[A-Za-z_]\w*\}?'),
        ('at', r'(?<=\s)--?[A-Za-z][\w-]*'),
        ('kw', r'(?m)^\s*(?:\$\s+)?(?:\./yii|php\s+yii|yii|composer|php|git|cd|mv|cp|rm|mkdir|chmod|chown|curl|wget|docker(?:-compose)?|npm|npx|sudo|apt(?:-get)?|brew|ls|cat|echo|export|source|vendor/bin/codecept|codecept|tests/bin/yii|java)\b'),
        ('nu', r'\b\d+\b'),
    ],
    'sql': [
        ('cm', r'--[^\n]*|/\*[\s\S]*?\*/'),
        ('st', r"'(?:[^'\\]|\\.)*'"),
        ('va', r'`[^`\n]*`|:\w+'),
        ('kw', '(?i)' + _alt(SQL_KEYWORDS)),
        ('nu', r'\b\d+(?:\.\d+)?\b'),
        ('fn', r'\b\w+(?=\()'),
    ],
    'json': [
        ('cm', r'//[^\n]*|/\*[\s\S]*?\*/'),
        ('pk', r'"(?:[^"\\]|\\.)*"(?=\s*:)'),
        ('st', r'"(?:[^"\\]|\\.)*"'),
        ('lt', r'\b(?:true|false|null)\b'),
        ('nu', r'-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b'),
    ],
    'yaml': [
        ('cm', r'#[^\n]*'),
        ('pk', r'(?m)^\s*-?\s*[\w.\-/]+(?=\s*:(?:\s|$))'),
        ('st', STR),
        ('lt', r'\b(?:true|false|null|yes|no|~)\b'),
        ('nu', r'\b\d+(?:\.\d+)?\b'),
        ('at', r'(?m)^\s*-(?=\s)'),
    ],
    'ini': [
        ('cm', r'(?m)^\s*[;#][^\n]*'),
        ('tg', r'(?m)^\s*\[[^\]]+\]'),
        ('pk', r'(?m)^\s*[\w.\-]+(?=\s*=)'),
        ('st', STR),
        ('lt', r'\b(?:true|false|on|off|yes|no|null)\b'),
        ('nu', r'\b\d+\b'),
    ],
    'nginx': [
        ('cm', r'#[^\n]*'),
        ('kw', r'(?m)^\s*[a-z_]+\b'),
        ('va', r'\$\w+'),
        ('st', STR),
        ('nu', r'\b\d+[kKmMgGsShHdD]?\b'),
        ('at', r'(?m)^\s*(?:location|server|http|upstream|events|if)\b'),
    ],
    'apache': [
        ('cm', r'#[^\n]*'),
        ('tg', r'</?\w+[^>\n]*>'),
        ('kw', r'(?m)^\s*[A-Z]\w+\b'),
        ('va', r'%\{[^}]+\}'),
        ('st', STR),
        ('at', r'!-[fdl]\b|\[[A-Z,=\d]+\]'),
    ],
    'css': [
        ('cm', r'/\*[\s\S]*?\*/'),
        ('at', r'@[\w-]+'),
        ('pk', r'[\w-]+(?=\s*:)'),
        ('st', STR),
        ('nu', r'#[0-9a-fA-F]{3,8}\b|\b\d+(?:\.\d+)?(?:px|em|rem|%|vh|vw|s|ms|deg)?\b'),
        ('fn', r'[\w-]+(?=\()'),
    ],
    'http': [
        ('kw', r'(?m)^(?:[A-Z]+ \S+ HTTP/[\d.]+|HTTP/[\d.]+ \d+[^\n]*)$'),
        ('pk', r'(?m)^[A-Za-z][\w-]*(?=:)'),
        ('nu', r'\b\d+\b'),
    ],
    'twig': [
        ('cm', r'\{#[\s\S]*?#\}|<!--[\s\S]*?-->'),
        ('tp', r'\{\{[\s\S]*?\}\}|\{%[\s\S]*?%\}'),
        ('tg', r'</?[A-Za-z][\w:-]*|/?>'),
        ('st', STR),
    ],
    'smarty': [
        ('cm', r'\{\*[\s\S]*?\*\}|<!--[\s\S]*?-->'),
        ('tp', r'\{[^{}\n]*\}'),
        ('tg', r'</?[A-Za-z][\w:-]*|/?>'),
        ('st', STR),
    ],
}

LANG_ALIASES = {
    'sh': 'bash', 'shell': 'bash', 'console': 'bash', 'zsh': 'bash', 'cmd': 'bash',
    'javascript': 'js', 'html': 'html', 'xml': 'html', 'yml': 'yaml',
    'apacheconf': 'apache', 'htaccess': 'apache', 'txt': 'text', 'plain': 'text',
    'text': 'text', '': 'text', 'mysql': 'sql', 'pgsql': 'sql', 'jsonc': 'json',
}
LANG_LABELS = {
    'php': 'PHP', 'js': 'JavaScript', 'bash': 'Консоль', 'sql': 'SQL', 'json': 'JSON',
    'yaml': 'YAML', 'ini': 'INI', 'nginx': 'nginx', 'apache': 'Apache', 'css': 'CSS',
    'http': 'HTTP', 'html': 'HTML', 'text': '', 'twig': 'Twig', 'smarty': 'Smarty',
    'diff': 'diff',
}

_COMPILED = {}


def _rules(lang):
    if lang not in _COMPILED:
        parts = []
        for i, (cls, pat) in enumerate(LANG_RULES[lang]):
            # выносим inline-флаги в начало объединённого выражения
            flags = ''
            m = re.match(r'\(\?([a-z]+)\)', pat)
            if m:
                flags = m.group(1)
                pat = pat[m.end():]
            parts.append('(?P<g%d>%s%s)' % (i, ('(?%s:' % flags) if flags else '(?:', pat + ')'))
        _COMPILED[lang] = (re.compile('|'.join(parts)), [c for c, _ in LANG_RULES[lang]])
    return _COMPILED[lang]


def _tokenize(code, lang):
    rx, classes = _rules(lang)
    out = []
    pos = 0
    for m in rx.finditer(code):
        if m.start() > pos:
            out.append(esc(code[pos:m.start()]))
        cls = classes[int(m.lastgroup[1:])]
        out.append('<span class="t-%s">%s</span>' % (cls, esc(m.group(0))))
        pos = m.end()
    out.append(esc(code[pos:]))
    return ''.join(out)


_HTML_TAG = re.compile(r'<!--[\s\S]*?-->|<!DOCTYPE[^>]*>|<(/?)([A-Za-z][\w:-]*)([^<>]*?)(/?)>')
_HTML_ATTR = re.compile(r'([\w:@.-]+)(\s*=\s*)("[^"]*"|\'[^\']*\'|[^\s"\'>]+)?')


def _hl_html(code):
    out = []
    pos = 0
    for m in _HTML_TAG.finditer(code):
        if m.start() > pos:
            out.append(esc(code[pos:m.start()]))
        s = m.group(0)
        if s.startswith('<!--'):
            out.append('<span class="t-cm">%s</span>' % esc(s))
        elif s.startswith('<!'):
            out.append('<span class="t-tg">%s</span>' % esc(s))
        else:
            close, name, attrs, selfclose = m.groups()
            body = ['<span class="t-tg">&lt;%s%s</span>' % (close, esc(name))]
            apos = 0
            for a in _HTML_ATTR.finditer(attrs):
                if a.start() > apos:
                    body.append(esc(attrs[apos:a.start()]))
                body.append('<span class="t-at">%s</span>' % esc(a.group(1)))
                if a.group(2):
                    body.append(esc(a.group(2)))
                if a.group(3):
                    body.append('<span class="t-st">%s</span>' % esc(a.group(3)))
                apos = a.end()
            body.append(esc(attrs[apos:]))
            body.append('<span class="t-tg">%s&gt;</span>' % selfclose)
            out.append(''.join(body))
        pos = m.end()
    out.append(esc(code[pos:]))
    return ''.join(out)


_PHP_REGION = re.compile(r'(<\?(?:php|=)?[\s\S]*?(?:\?>|\Z))')


def highlight(code, lang):
    lang = LANG_ALIASES.get(lang, lang)
    if lang == 'text':
        return esc(code)
    if lang == 'diff':
        lines = []
        for ln in code.split('\n'):
            if ln.startswith('+') and not ln.startswith('+++'):
                lines.append('<span class="t-ins">%s</span>' % esc(ln))
            elif ln.startswith('-') and not ln.startswith('---'):
                lines.append('<span class="t-del">%s</span>' % esc(ln))
            elif ln.startswith('@@'):
                lines.append('<span class="t-cm">%s</span>' % esc(ln))
            else:
                lines.append(esc(ln))
        return '\n'.join(lines)
    if lang == 'html':
        return _hl_html(code)
    if lang == 'php':
        if '<?' not in code:
            return _tokenize(code, 'php')
        out = []
        for part in _PHP_REGION.split(code):
            if not part:
                continue
            if part.startswith('<?'):
                out.append(_tokenize(part, 'php'))
            else:
                out.append(_hl_html(part))
        return ''.join(out)
    if lang in LANG_RULES:
        return _tokenize(code, lang)
    return esc(code)


# --------------------------------------------------------------------------- markdown

CALLOUTS = {
    'NOTE': ('note', 'На заметку'),
    'TIP': ('tip', 'Совет'),
    'WARNING': ('warning', 'Внимание'),
    'GOTCHA': ('gotcha', 'Грабли'),
    'WHY': ('why', 'Зачем это нужно'),
    'EXAMPLE': ('example', 'Пример из жизни'),
}

BLOCK_TAGS = ('div', 'svg', 'figure', 'details', 'section', 'table', 'p', 'ul', 'ol',
              'blockquote', 'pre', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'aside',
              'nav', 'dl', 'iframe', 'video', 'img', 'kbd-table', 'article', '!--')
INLINE_TAGS = 'kbd|br|sup|sub|mark|small|abbr|span|b|i|u|em|strong|code|s|del|ins|wbr'

FENCE_RE = re.compile(r'^(\s*)(`{3,}|~{3,})\s*([\w+-]*)\s*(.*)$')
CONTAINER_RE = re.compile(r'^:::\s*([\w-]+)\s*(.*)$')
HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*(?:\{#([\w-]+)\})?\s*#*\s*$')
HR_RE = re.compile(r'^\s*([-*_])(?:\s*\1){2,}\s*$')
LIST_RE = re.compile(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$')
TABLE_SEP_RE = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$')


class Renderer:
    """Markdown → HTML для одной страницы. Попутно собирает заголовки и индекс поиска."""

    def __init__(self, page_id, known_pages, warn):
        self.page_id = page_id
        self.known = known_pages
        self.warn = warn
        self.headings = []          # (level, text_html, slug)
        self.slugs = set()
        self.sections = []          # для поиска: dict(a, h, text, code)
        self._open_section('', '')
        self.words = 0

    # ---- сбор данных для поиска

    def _open_section(self, anchor, heading):
        self.cur = {'a': anchor, 'h': heading, 'text': [], 'code': []}
        self.sections.append(self.cur)

    def _note_text(self, html_text):
        plain = strip_tags(html_text).strip()
        if plain:
            self.cur['text'].append(plain)
            self.words += len(plain.split())

    def _note_code(self, code):
        toks = set(re.findall(r'[A-Za-z_][\w:\\>$-]{2,}', code))
        self.cur['code'].extend(sorted(toks))

    # ---- inline

    def inline(self, text):
        stash = []

        def keep(s):
            stash.append(s)
            return '\x00%d\x00' % (len(stash) - 1)

        # code spans
        text = re.sub(r'``(.+?)``|`([^`\n]+)`',
                      lambda m: keep('<code>%s</code>' % esc((m.group(1) or m.group(2)).strip())),
                      text)
        # разрешённые inline-теги оставляем как есть
        text = re.sub(r'</?(?:%s)(?:\s[^<>]*)?/?>' % INLINE_TAGS, lambda m: keep(m.group(0)), text)
        text = esc(text)
        # картинки
        text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)',
                      lambda m: keep('<img src="%s" alt="%s"%s loading="lazy">' % (
                          attr(m.group(2)), attr(m.group(1)),
                          ' title="%s"' % attr(m.group(3)) if m.group(3) else '')),
                      text)
        # ссылки
        text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)',
                      lambda m: keep(self.link(m.group(1), m.group(2), m.group(3))), text)
        # автоссылки
        text = re.sub(r'&lt;(https?://[^\s&]+)&gt;',
                      lambda m: keep('<a href="%s" target="_blank" rel="noopener">%s</a>' % (
                          attr(m.group(1)), m.group(1))), text)
        # оформление
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', text)
        text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
        text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
        text = re.sub(r'\[\[kbd:([^\]]+)\]\]', r'<kbd>\1</kbd>', text)
        text = text.replace(' --- ', ' — ').replace(' -- ', ' — ')
        text = re.sub(r'(?<=\S)  \n', '<br>\n', text)
        # восстановить
        text = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], text)
        return text

    def link(self, label, href, title=None):
        label = label  # уже экранирован
        t = ' title="%s"' % attr(title) if title else ''
        if href.startswith('guide:'):
            slug = href[6:]
            return '<a href="%s" class="ext guide" target="_blank" rel="noopener"%s>%s</a>' % (
                GUIDE_URL % slug, t, label)
        if href.startswith('api:'):
            cls = href[4:]
            slug = re.sub(r'[\\/]', '-', cls).lower()
            slug = re.sub(r'::\$?', '#', slug)
            if '#' in slug:
                base, member = slug.split('#', 1)
                url = API_URL % (base + '.html#' + member + ('()' if member and not member.startswith('$') else '') + '-detail')
            else:
                url = API_URL % (slug + '.html')
            return '<a href="%s" class="ext api" target="_blank" rel="noopener"%s>%s</a>' % (url, t, label)
        if re.match(r'^[a-z]+://', href) or href.startswith('mailto:'):
            return '<a href="%s" class="ext" target="_blank" rel="noopener"%s>%s</a>' % (attr(href), t, label)
        if href.startswith('#'):
            return '<a href="%s"%s>%s</a>' % (attr(href), t, label)
        page, _, anchor = href.partition('#')
        if page.endswith('.html'):
            page = page[:-5]
        if page in self.known:
            url = page + '.html' + ('#' + anchor if anchor else '')
            return '<a href="%s" class="int"%s>%s</a>' % (attr(url), t, label)
        self.warn('%s: неизвестная ссылка [%s](%s)' % (self.page_id, strip_tags(label), href))
        return '<a href="%s"%s>%s</a>' % (attr(href), t, label)

    # ---- blocks

    def render(self, text):
        return self.blocks(text.replace('\r\n', '\n').split('\n'))

    def blocks(self, lines, cards=False):
        out = []
        i, n = 0, len(lines)
        while i < n:
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            m = FENCE_RE.match(line)
            if m:
                indent, fence, lang, meta = m.groups()
                j = i + 1
                while j < n and not re.match(r'^\s{0,%d}%s\s*$' % (len(indent), re.escape(fence[0]) + '{%d,}' % len(fence)), lines[j]):
                    j += 1
                code = [l[len(indent):] if l.startswith(indent) else l.lstrip() for l in lines[i + 1:j]]
                out.append(self.codeblock('\n'.join(code), lang, meta))
                i = j + 1
                continue
            m = CONTAINER_RE.match(line)
            if m:
                name, args = m.group(1), m.group(2).strip()
                depth, j = 1, i + 1
                while j < n:
                    if CONTAINER_RE.match(lines[j]):
                        depth += 1
                    elif lines[j].strip() == ':::':
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                out.append(self.container(name, args, lines[i + 1:j]))
                i = j + 1
                continue
            m = HEADING_RE.match(line)
            if m:
                out.append(self.heading(len(m.group(1)), m.group(2), m.group(3)))
                i += 1
                continue
            if HR_RE.match(line):
                out.append('<hr>')
                i += 1
                continue
            if line.startswith('>'):
                j = i
                inner = []
                while j < n and lines[j].startswith('>'):
                    inner.append(re.sub(r'^> ?', '', lines[j]))
                    j += 1
                out.append(self.quote(inner))
                i = j
                continue
            if '|' in line and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
                j = i + 2
                while j < n and lines[j].strip() and '|' in lines[j]:
                    j += 1
                out.append(self.table(lines[i], lines[i + 2:j]))
                i = j
                continue
            m = LIST_RE.match(line)
            if m:
                block, i = self.list_block(lines, i, cards)
                out.append(block)
                continue
            if re.match(r'^\s*<(?:%s)[\s>]' % '|'.join(re.escape(t) for t in BLOCK_TAGS), line) or line.startswith('<!--'):
                j = i
                raw = []
                while j < n and lines[j].strip():
                    raw.append(lines[j])
                    j += 1
                out.append('\n'.join(raw))
                i = j
                continue
            # параграф
            j = i
            para = []
            while j < n and lines[j].strip() and not self._starts_block(lines[j]):
                para.append(lines[j])
                j += 1
            if not para:
                para, j = [lines[i]], i + 1
            html_p = self.inline('\n'.join(para))
            self._note_text(html_p)
            out.append('<p>%s</p>' % html_p)
            i = j
        return '\n'.join(out)

    def _starts_block(self, line):
        return bool(FENCE_RE.match(line) or CONTAINER_RE.match(line) or HEADING_RE.match(line)
                    or line.startswith('>') or HR_RE.match(line) or LIST_RE.match(line)
                    or line.strip() == ':::')

    def heading(self, level, text, custom_id=None):
        text_html = self.inline(text)
        slug = custom_id or slugify(text)
        base, k = slug, 2
        while slug in self.slugs:
            slug = '%s-%d' % (base, k)
            k += 1
        self.slugs.add(slug)
        if level in (2, 3):
            self.headings.append((level, text_html, slug))
            self._open_section(slug, strip_tags(text_html))
        else:
            self._note_text(text_html)
        return '<h%d id="%s">%s<a class="anchor" href="#%s" aria-label="Ссылка на раздел">#</a></h%d>' % (
            level, slug, text_html, slug, level)

    def codeblock(self, code, lang, meta):
        code = code.rstrip('\n')
        lang = (lang or '').lower()
        norm = LANG_ALIASES.get(lang, lang)
        title = ''
        m = re.search(r'title="([^"]*)"', meta or '')
        if m:
            title = m.group(1)
        hl_lines = set()
        m = re.search(r'\{([\d,\-\s]+)\}', meta or '')
        if m:
            for part in m.group(1).split(','):
                part = part.strip()
                if '-' in part:
                    a, b = part.split('-')
                    hl_lines.update(range(int(a), int(b) + 1))
                elif part:
                    hl_lines.add(int(part))
        self._note_code(code)
        body = highlight(code, lang)
        if hl_lines:
            lines = body.split('\n')
            lines = ['<span class="hl-line">%s</span>' % l if (k + 1) in hl_lines else l
                     for k, l in enumerate(lines)]
            body = '\n'.join(lines)
        label = LANG_LABELS.get(norm, lang)
        head = ''
        if title or label:
            head = '<div class="code-head">%s<span class="code-lang">%s</span></div>' % (
                ('<span class="code-title">%s</span>' % esc(title)) if title else '', esc(label))
        return ('<figure class="code" data-lang="%s">%s<button type="button" class="copy" '
                'aria-label="Копировать код" title="Копировать">Копировать</button>'
                '<pre><code>%s</code></pre></figure>' % (attr(norm), head, body))

    def quote(self, inner):
        if inner:
            m = re.match(r'^\[!(\w+)\]\s*(.*)$', inner[0])
            if m and m.group(1).upper() in CALLOUTS:
                cls, default_title = CALLOUTS[m.group(1).upper()]
                title = m.group(2).strip() or default_title
                body = self.blocks(inner[1:])
                return ('<aside class="callout %s"><div class="callout-title">%s</div>'
                        '<div class="callout-body">%s</div></aside>' % (cls, self.inline(title), body))
        return '<blockquote>%s</blockquote>' % self.blocks(inner)

    @staticmethod
    def _split_row(line):
        cells, cur, in_code = [], [], False
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|') and not line.endswith('\\|'):
            line = line[:-1]
        k = 0
        while k < len(line):
            ch = line[k]
            if ch == '\\' and k + 1 < len(line) and line[k + 1] == '|':
                cur.append('|')
                k += 2
                continue
            if ch == '`':
                in_code = not in_code
            if ch == '|' and not in_code:
                cells.append(''.join(cur).strip())
                cur = []
            else:
                cur.append(ch)
            k += 1
        cells.append(''.join(cur).strip())
        return cells

    def table(self, head, rows):
        heads = self._split_row(head)
        out = ['<div class="table-wrap"><table>', '<thead><tr>']
        for h in heads:
            out.append('<th>%s</th>' % self.inline(h))
            self._note_text(h)
        out.append('</tr></thead><tbody>')
        for r in rows:
            cells = self._split_row(r)
            cells += [''] * (len(heads) - len(cells))
            out.append('<tr>' + ''.join('<td>%s</td>' % self.inline(c) for c in cells[:len(heads)]) + '</tr>')
            self._note_text(' '.join(cells))
        out.append('</tbody></table></div>')
        return '\n'.join(out)

    def list_block(self, lines, i, cards=False):
        n = len(lines)
        m = LIST_RE.match(lines[i])
        indent = len(m.group(1))
        ordered = m.group(2)[0].isdigit()
        start = int(m.group(2)[:-1]) if ordered else 1
        items = []
        cur = None
        while i < n:
            line = lines[i]
            if not line.strip():
                # пустая строка: список продолжается, если дальше вложенное содержимое или новый пункт
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and (LIST_RE.match(lines[j]) and len(LIST_RE.match(lines[j]).group(1)) == indent
                              or (len(lines[j]) - len(lines[j].lstrip()) > indent)):
                    if cur is not None:
                        cur.append('')
                    i = j
                    continue
                break
            m = LIST_RE.match(line)
            if m and len(m.group(1)) == indent and (m.group(2)[0].isdigit() == ordered):
                cur = [m.group(3)]
                items.append((cur, len(m.group(1)) + len(m.group(2)) + 1))
                i += 1
                continue
            lead = len(line) - len(line.lstrip())
            if cur is not None and lead > indent:
                cur.append(line[min(lead, items[-1][1]):])
                i += 1
                continue
            break
        parts = []
        for content, _ in items:
            h = self.blocks(content)
            if cards:
                mm = re.match(r'^<p><strong>(.+?)</strong>\s*(?:[—–:-]\s*)?(.*)$', h, re.S)
                if mm:
                    rest = mm.group(2)
                    h = '<div class="card-title">%s</div>' % mm.group(1) + (('<p>' + rest) if rest.strip() != '</p>' else '')
                parts.append('<div class="card">%s</div>' % h)
            else:
                if h.count('<p>') == 1 and h.startswith('<p>') and h.endswith('</p>'):
                    h = h[3:-4]
                parts.append('<li>%s</li>' % h)
        if cards:
            return '<div class="cards">%s</div>' % ''.join(parts), i
        tag = 'ol' if ordered else 'ul'
        attrs = ' start="%d"' % start if ordered and start != 1 else ''
        return '<%s%s>\n%s\n</%s>' % (tag, attrs, '\n'.join(parts), tag), i

    # ---- containers

    def container(self, name, args, inner):
        if name == 'tabs':
            return self.tabs(inner, args)
        if name == 'cols':
            return self.cols(inner)
        if name == 'quiz':
            return self.quiz(inner, args)
        if name == 'diagram':
            return self.diagram(args, inner)
        if name == 'details':
            return '<details class="details"><summary>%s</summary><div class="details-body">%s</div></details>' % (
                self.inline(args or 'Подробнее'), self.blocks(inner))
        if name == 'cards':
            return self.blocks(inner, cards=True)
        if name == 'steps':
            return '<div class="steps">%s</div>' % self.blocks(inner)
        if name == 'lead':
            return '<div class="lead">%s</div>' % self.blocks(inner)
        if name == 'compact':
            return '<div class="compact">%s</div>' % self.blocks(inner)
        if name == 'kv':
            return self.kv(inner)
        self.warn('%s: неизвестный контейнер :::%s' % (self.page_id, name))
        return self.blocks(inner)

    @staticmethod
    def _split_sections(inner):
        groups, label, buf = [], None, []
        for line in inner:
            m = re.match(r'^===\s+(.*)$', line)
            if m:
                if label is not None or buf and any(l.strip() for l in buf):
                    groups.append((label or '', buf))
                label, buf = m.group(1).strip(), []
            else:
                buf.append(line)
        groups.append((label or '', buf))
        return groups

    def tabs(self, inner, args):
        groups = self._split_sections(inner)
        gid = 'tabs-%s' % hashlib.md5(''.join(inner).encode('utf-8')).hexdigest()[:8]
        heads, panels = [], []
        for k, (label, body) in enumerate(groups):
            heads.append('<button type="button" role="tab" class="tab%s" aria-selected="%s" data-tab="%d">%s</button>' % (
                ' active' if k == 0 else '', 'true' if k == 0 else 'false', k, self.inline(label)))
            panels.append('<div role="tabpanel" class="tab-panel%s" data-tab="%d">%s</div>' % (
                ' active' if k == 0 else '', k, self.blocks(body)))
        return '<div class="tabs" id="%s"><div class="tab-list" role="tablist">%s</div>%s</div>' % (
            gid, ''.join(heads), ''.join(panels))

    def cols(self, inner):
        groups = self._split_sections(inner)
        cols = []
        for label, body in groups:
            cls = ''
            low = label.lower()
            if low.startswith(('плохо', 'было', 'не так', 'yii 1', '✗', '❌')):
                cls = ' bad'
            elif low.startswith(('хорошо', 'стало', 'так', 'yii 2', '✓', '✅')):
                cls = ' good'
            cols.append('<div class="col%s">%s%s</div>' % (
                cls, '<div class="col-label">%s</div>' % self.inline(label) if label else '', self.blocks(body)))
        return '<div class="cols">%s</div>' % ''.join(cols)

    def quiz(self, inner, args):
        cards, q, a, mode = [], [], [], None
        for line in inner:
            if line.startswith('Q:'):
                if q:
                    cards.append((q, a))
                q, a, mode = [line[2:].strip()], [], 'q'
            elif line.startswith('A:'):
                a, mode = [line[2:].strip()], 'a'
            elif mode == 'q':
                q.append(line)
            elif mode == 'a':
                a.append(line)
        if q:
            cards.append((q, a))
        out = ['<div class="quiz"><div class="quiz-head"><span class="quiz-title">%s</span>'
               '<span class="quiz-count">%d</span>'
               '<button type="button" class="quiz-all">Раскрыть все</button></div><div class="quiz-cards">' % (
                   self.inline(args or 'Проверь себя'), len(cards))]
        for k, (qq, aa) in enumerate(cards):
            qh = self.blocks(qq)
            ah = self.blocks(aa)
            self._note_text(qh)
            out.append('<div class="qcard"><button type="button" class="qcard-q" aria-expanded="false">'
                       '<span class="qcard-n">%d</span><span class="qcard-text">%s</span>'
                       '<span class="qcard-arrow" aria-hidden="true"></span></button>'
                       '<div class="qcard-a">%s</div></div>' % (k + 1, qh, ah))
        out.append('</div></div>')
        return ''.join(out)

    def diagram(self, name, inner):
        path = os.path.join(DIAGRAMS, name + '.svg')
        if not os.path.exists(path):
            self.warn('%s: нет диаграммы %s' % (self.page_id, name))
            return ''
        svg = read(path).strip()
        cap = self.blocks(inner)
        return '<figure class="diagram diagram-%s">%s%s</figure>' % (
            attr(name), svg, ('<figcaption>%s</figcaption>' % cap) if cap.strip() else '')

    def kv(self, inner):
        """Компактный список «ключ — значение»: строки вида `ключ` — описание."""
        rows = []
        for line in inner:
            if not line.strip():
                continue
            m = re.match(r'^(.+?)\s+[—–-]\s+(.*)$', line)
            if m:
                rows.append('<div class="kv-row"><div class="kv-key">%s</div><div class="kv-val">%s</div></div>' % (
                    self.inline(m.group(1)), self.inline(m.group(2))))
                self._note_text(m.group(1) + ' ' + m.group(2))
            else:
                rows.append('<div class="kv-row"><div class="kv-key"></div><div class="kv-val">%s</div></div>' % self.inline(line))
        return '<div class="kv">%s</div>' % ''.join(rows)


# --------------------------------------------------------------------------- content loading

def parse_front_matter(text, path):
    if not text.startswith('---'):
        raise SystemExit('%s: нет front matter' % path)
    end = text.find('\n---', 3)
    if end < 0:
        raise SystemExit('%s: не закрыт front matter' % path)
    meta = {}
    for line in text[3:end].strip().split('\n'):
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        meta[k.strip()] = v.strip()
    body = text[end + 4:]
    return meta, body


def load_pages():
    pages = []
    for fname in sorted(os.listdir(CONTENT)):
        if not fname.endswith('.md'):
            continue
        path = os.path.join(CONTENT, fname)
        meta, body = parse_front_matter(read(path), path)
        pid = meta.get('id') or re.sub(r'^\d+-', '', fname[:-3])
        meta['sources'] = [s.strip() for s in meta.get('sources', '').split(',') if s.strip()]
        meta['tags'] = [s.strip() for s in meta.get('tags', '').split(',') if s.strip()]
        pages.append({'id': pid, 'meta': meta, 'body': body, 'file': fname})
    return pages


def load_parts():
    return json.load(open(os.path.join(SRC, 'parts.json'), encoding='utf-8'))


def load_chapters():
    return json.load(open(os.path.join(SRC, 'guide-chapters.json'), encoding='utf-8'))


# --------------------------------------------------------------------------- templates

def template(name):
    return read(os.path.join(TEMPLATES, name))


def fill(tpl, mapping):
    def sub(m):
        key = m.group(1)
        if key not in mapping:
            raise SystemExit('в шаблоне нет значения для {{%s}}' % key)
        return mapping[key]
    return re.sub(r'\{\{(\w+)\}\}', sub, tpl)


# --------------------------------------------------------------------------- site build

ICON_CHECK = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3 3 7-7" fill="none" '
              'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def build_nav(parts, pages_by_part, current_id):
    out = ['<nav class="nav" aria-label="Разделы">']
    out.append('<a class="nav-home%s" href="index.html">Главная</a>' % (' active' if current_id == 'index' else ''))
    for part in parts:
        pages = pages_by_part.get(part['id'], [])
        if not pages:
            continue
        out.append('<div class="nav-part"><div class="nav-part-title"><span class="nav-part-icon">%s</span>%s</div><ul>' % (
            part.get('icon', ''), esc(part['title'])))
        for p in pages:
            out.append('<li><a href="%s.html" class="nav-link%s" data-page="%s"%s>'
                       '<span class="nav-num">%s</span><span class="nav-text">%s</span>'
                       '<span class="nav-done" aria-hidden="true">%s</span></a></li>' % (
                           p['id'], ' active' if p['id'] == current_id else '', p['id'],
                           ' aria-current="page"' if p['id'] == current_id else '',
                           p['num'], esc(p['meta']['title']), ICON_CHECK))
        out.append('</ul></div>')
    out.append('<div class="nav-part"><div class="nav-part-title"><span class="nav-part-icon">⌘</span>Ещё</div><ul>')
    for pid, title in (('all', 'Всё одной страницей'),):
        out.append('<li><a href="%s.html" class="nav-link%s" data-page="%s"><span class="nav-num">∞</span>'
                   '<span class="nav-text">%s</span></a></li>' % (pid, ' active' if current_id == pid else '', pid, title))
    out.append('</ul></div></nav>')
    return '\n'.join(out)


def build_toc(headings):
    if not headings:
        return ''
    out = ['<div class="toc-title">На этой странице</div><ul class="toc-list">']
    for level, text, slug in headings:
        out.append('<li class="toc-l%d"><a href="#%s">%s</a></li>' % (level, slug, strip_tags(text) and esc(strip_tags(text))))
    out.append('</ul>')
    return '\n'.join(out)


def reading_time(words, code_lines):
    minutes = words / 150.0 + code_lines / 45.0
    return max(1, int(round(minutes)))


def main():
    check_only = '--check' in sys.argv
    warnings = []

    def warn(msg):
        warnings.append(msg)

    parts = load_parts()
    part_by_id = {p['id']: p for p in parts}
    pages = load_pages()
    chapters = load_chapters()
    chapter_by_slug = {c['slug']: c for c in chapters}
    known = {p['id'] for p in pages} | {'index', 'all'}

    # порядок и нумерация
    pages_by_part = {}
    for p in pages:
        part = p['meta'].get('part')
        if part not in part_by_id:
            raise SystemExit('%s: неизвестная часть "%s"' % (p['file'], part))
        pages_by_part.setdefault(part, []).append(p)
    ordered = []
    for part in parts:
        for p in pages_by_part.get(part['id'], []):
            p['part'] = part
            ordered.append(p)
    for k, p in enumerate(ordered):
        p['num'] = '%02d' % (k + 1)
        p['index'] = k

    # рендер
    search_index = []
    covered = {}
    for p in ordered:
        r = Renderer(p['id'], known, warn)
        p['html'] = r.render(p['body'])
        p['headings'] = r.headings
        code_text = ''.join(re.findall(r'```[\s\S]*?```', p['body']))
        p['minutes'] = reading_time(r.words, code_text.count('\n'))
        for s in r.sections:
            text = ' '.join(s['text'])
            code = ' '.join(dict.fromkeys(s['code']))
            if not text and not code and not s['h']:
                continue
            search_index.append({
                'p': p['meta']['title'], 'u': p['id'] + '.html', 'a': s['a'], 'h': s['h'],
                't': text[:500], 'c': code[:400], 'g': p['part']['title'],
            })
        for slug in p['meta']['sources']:
            if slug not in chapter_by_slug:
                warn('%s: неизвестная глава руководства "%s"' % (p['file'], slug))
            covered.setdefault(slug, []).append(p['id'])

    missing = [c for c in chapters if c['slug'] not in covered]
    if missing:
        warn('главы руководства без раздела: ' + ', '.join(c['slug'] for c in missing))

    if warnings:
        print('Предупреждения:')
        for w in warnings:
            print('  - ' + w)
    print('Страниц: %d, глав руководства покрыто: %d/%d, записей в поиске: %d' % (
        len(ordered), len(chapters) - len(missing), len(chapters), len(search_index)))
    if check_only:
        return 1 if warnings else 0

    # выходная папка
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        path = os.path.join(OUT, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copytree(ASSETS, os.path.join(OUT, 'assets'))
    if os.path.isdir(ARCHIVE):          # прежние версии сайта: src/archive/v1 → docs/v1
        for name in sorted(os.listdir(ARCHIVE)):
            shutil.copytree(os.path.join(ARCHIVE, name), os.path.join(OUT, name))
    write(os.path.join(OUT, '.nojekyll'), '')

    base = template('base.html')
    page_tpl = template('page.html')
    index_tpl = template('index.html')
    all_tpl = template('all.html')

    def shell(title, description, body_class, sidebar, main, toc, page_id):
        return fill(base, {
            'title': esc(title), 'site': esc(SITE_NAME), 'description': attr(description),
            'body_class': body_class, 'sidebar': sidebar, 'main': main, 'toc': toc,
            'page_id': page_id,
        })

    # страницы разделов
    for p in ordered:
        meta = p['meta']
        prev_p = ordered[p['index'] - 1] if p['index'] > 0 else None
        next_p = ordered[p['index'] + 1] if p['index'] + 1 < len(ordered) else None
        sources = []
        for slug in meta['sources']:
            ch = chapter_by_slug.get(slug)
            if ch:
                sources.append('<li><a href="%s" target="_blank" rel="noopener"><span class="src-part">%s</span>%s</a></li>' % (
                    GUIDE_URL % slug, esc(ch['part']), esc(ch['title'])))
        main = fill(page_tpl, {
            'part_icon': p['part'].get('icon', ''),
            'part_title': esc(p['part']['title']),
            'num': p['num'],
            'title': esc(meta['title']),
            'summary': esc(meta.get('summary', '')),
            'minutes': str(p['minutes']),
            'chapters_meta': ('<span class="meta-item" title="Сколько глав руководства сжато в этот раздел">📚 %d %s руководства</span>'
                              % (len(sources), plural(len(sources), 'глава', 'главы', 'глав'))) if sources
                             else '<span class="meta-item" title="Составлено по всем разделам сайта">🧷 сводный раздел</span>',
            'page_id': p['id'],
            'body': p['html'],
            'sources_block': ('<details class="sources"><summary>Источник: главы официального руководства</summary><ul>%s</ul></details>'
                              % ''.join(sources)) if sources else '',
            'prev': ('<a class="pager-link prev" href="%s.html"><span class="pager-label">← Назад</span>'
                     '<span class="pager-title">%s</span></a>' % (prev_p['id'], esc(prev_p['meta']['title']))) if prev_p else '<span></span>',
            'next': ('<a class="pager-link next" href="%s.html"><span class="pager-label">Дальше →</span>'
                     '<span class="pager-title">%s</span></a>' % (next_p['id'], esc(next_p['meta']['title']))) if next_p else '<span></span>',
        })
        html_out = shell(meta['title'] + ' · ' + SITE_NAME, meta.get('summary', ''), 'page',
                         build_nav(parts, pages_by_part, p['id']), main, build_toc(p['headings']), p['id'])
        write(os.path.join(OUT, p['id'] + '.html'), html_out)

    # главная
    parts_html = []
    for part in parts:
        pl = pages_by_part.get(part['id'], [])
        if not pl:
            continue
        items = ''.join('<li><a href="%s.html" data-page="%s"><span class="nav-num">%s</span>%s<span class="nav-done">%s</span></a></li>' % (
            p['id'], p['id'], p['num'], esc(p['meta']['title']), ICON_CHECK) for p in pl)
        parts_html.append('<section class="part-card" id="part-%s"><div class="part-card-head">'
                          '<span class="part-card-icon">%s</span><div><h3>%s</h3><p>%s</p></div></div><ul>%s</ul></section>' % (
                              part['id'], part.get('icon', ''), esc(part['title']), esc(part.get('blurb', '')), items))
    total_minutes = sum(p['minutes'] for p in ordered)
    hero_code = highlight(
        "class PostController extends Controller\n"
        "{\n"
        "    public function actionView($id)\n"
        "    {\n"
        "        $post = Post::findOne($id)\n"
        "            ?? throw new NotFoundHttpException();\n"
        "\n"
        "        return $this->render('view', ['post' => $post]);\n"
        "    }\n"
        "}\n"
        "\n"
        "// Active Record: таблица = класс, строка = объект\n"
        "$posts = Post::find()\n"
        "    ->where(['status' => Post::STATUS_PUBLISHED])\n"
        "    ->with('author', 'tags')\n"
        "    ->orderBy(['created_at' => SORT_DESC])\n"
        "    ->limit(10)\n"
        "    ->all();", 'php')
    index_main = fill(index_tpl, {
        'hero_code': hero_code,
        'parts': ''.join(parts_html),
        'pages_count': str(len(ordered)),
        'chapters_count': str(len(chapters)),
        'minutes': str(total_minutes),
        'hours': ('%d ч' % round(total_minutes / 60.0)) if total_minutes >= 90 else ('%d мин' % total_minutes),
        'lifecycle': read(os.path.join(DIAGRAMS, 'request-lifecycle.svg')) if os.path.exists(os.path.join(DIAGRAMS, 'request-lifecycle.svg')) else '',
    })
    write(os.path.join(OUT, 'index.html'), shell(SITE_NAME,
                                                 'Все главы руководства Yii 2.0 в компактных разделах с примерами кода.',
                                                 'home', build_nav(parts, pages_by_part, 'index'), index_main, '', 'index'))

    # всё одной страницей
    all_body = []
    all_toc = []
    for part in parts:
        pl = pages_by_part.get(part['id'], [])
        if not pl:
            continue
        all_body.append('<h1 class="all-part" id="part-%s">%s %s</h1>' % (part['id'], part.get('icon', ''), esc(part['title'])))
        all_toc.append('<li class="toc-l2"><a href="#part-%s">%s</a></li>' % (part['id'], esc(part['title'])))
        for p in pl:
            body = re.sub(r'\bid="([\w-]+)"', lambda m: 'id="%s--%s"' % (p['id'], m.group(1)), p['html'])
            body = re.sub(r'href="#([\w-]+)"', lambda m: 'href="#%s--%s"' % (p['id'], m.group(1)), body)
            body = re.sub(r'href="([\w-]+)\.html#([\w-]+)"', r'href="#\1--\2"', body)
            body = re.sub(r'href="([\w-]+)\.html"', r'href="#\1"', body)
            all_body.append('<section class="all-page" id="%s"><h2 class="all-title"><span class="nav-num">%s</span>%s</h2>'
                            '<p class="all-summary">%s</p>%s</section>' % (
                                p['id'], p['num'], esc(p['meta']['title']), esc(p['meta'].get('summary', '')), body))
            all_toc.append('<li class="toc-l3"><a href="#%s">%s</a></li>' % (p['id'], esc(p['meta']['title'])))
    all_main = fill(all_tpl, {'body': '\n'.join(all_body), 'pages_count': str(len(ordered))})
    write(os.path.join(OUT, 'all.html'), shell('Всё одной страницей · ' + SITE_NAME,
                                               'Все разделы шпаргалки на одной странице: для поиска по Ctrl+F и печати.',
                                               'all', build_nav(parts, pages_by_part, 'all'), all_main,
                                               '<div class="toc-title">Разделы</div><ul class="toc-list">%s</ul>' % ''.join(all_toc), 'all'))

    # поиск и данные
    write(os.path.join(OUT, 'assets', 'search-index.js'),
          'window.SEARCH_INDEX=' + json.dumps(search_index, ensure_ascii=False, separators=(',', ':')) + ';\n'
          'window.PAGE_LIST=' + json.dumps([{'id': p['id'], 't': p['meta']['title'], 'g': p['part']['id']} for p in ordered],
                                             ensure_ascii=False, separators=(',', ':')) + ';\n')
    write(os.path.join(OUT, '404.html'), fill(template('404.html'), {'site': esc(SITE_NAME)}))
    explorer = os.path.join(ROOT, 'build_explorer.py')
    if os.path.exists(explorer):
        # docs/ очищается выше, поэтому каталог механизмов пересобираем следом
        subprocess.run([sys.executable, explorer], check=True)

    print('Готово: %s' % OUT)
    return 0


def plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 19:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


if __name__ == '__main__':
    sys.exit(main())
