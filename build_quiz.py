# -*- coding: utf-8 -*-
"""Сборка страницы «Проверка знаний Yii 2» из src/quiz/.

    python3 build_quiz.py

Пишет docs/quiz.html и src/quiz/_fragment.html.

Вопросы уезжают в страницу готовой разметкой: подсветка кода и инлайновый
`код` делаются здесь, в браузере остаётся только перемешивание и подсчёт.
Заодно сверяются ссылки: каждая обязана вести на существующую страницу
курса и на существующий узел справочника.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'quiz')
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, ROOT)

import catalog                                  # noqa: E402  общий движок страниц
import build as site                            # noqa: E402  подсветка кода
import content as data                          # noqa: E402
from catalog import attr, esc, inline           # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'quiz.html')
FRAGMENT = os.path.join(SRC, '_fragment.html')

TITLE = 'Проверка знаний Yii 2'
DESCRIPTION = ('Вопросы по Yii 2 с разбором: быстрый прогон, экзамен, тренировка по теме '
               'и работа над ошибками. Ответы к вопросам про код проверены на самом фреймворке.')
GROUP_COLOR = {
    'http': 'var(--g-http)',
    'data': 'var(--g-data)',
    'db': 'var(--g-db)',
    'view': 'var(--g-view)',
    'object': 'var(--g-object)',
}


def course_pages():
    """Идентификаторы страниц курса — по именам файлов src/content/NN-имя.md."""
    d = os.path.join(ROOT, 'src', 'content')
    out = set()
    for name in os.listdir(d):
        m = re.match(r'^\d+-(.+)\.md$', name)
        if m:
            out.add(m.group(1))
    return out


def explorer_topics():
    """Узлы справочника: id → заголовок. Модуль содержимого там тоже content.py."""
    import importlib.util

    path = os.path.join(ROOT, 'src', 'explorer', 'content.py')
    if not os.path.exists(path):
        return {}
    spec = importlib.util.spec_from_file_location('explorer_content', path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(ROOT, 'src', 'explorer'))
    spec.loader.exec_module(mod)
    return {t['id']: t['title'] for t in mod.TOPICS}


def check(questions, pages, nodes):
    """Всё, что можно поймать до публикации, ловим здесь."""
    topics = {t['id'] for t in data.TOPICS}
    seen = set()
    texts = {}
    for q in questions:
        where = q.get('id', '(без id)')
        assert q.get('id'), 'вопрос без id: %r' % q.get('text', '')[:60]
        assert q['id'] not in seen, 'повторяющийся id: %s' % q['id']
        seen.add(q['id'])
        # одинаковые формулировки путают и читателя, и разбор ошибок в конце
        assert q['text'] not in texts, 'повторяющаяся формулировка: %s и %s' % (texts[q['text']], q['id'])
        texts[q['text']] = q['id']
        assert q['topic'] in topics, '%s: неизвестная тема %s' % (where, q['topic'])

        opts = q['options']
        assert len(opts) >= 2, '%s: вариантов меньше двух' % where
        assert len(set(opts)) == len(opts), '%s: варианты повторяются' % where

        ans = q['answer']
        ans = ans if isinstance(ans, list) else [ans]
        assert ans, '%s: не указан верный вариант' % where
        for i in ans:
            assert 0 <= i < len(opts), '%s: ответ %d вне списка вариантов' % (where, i)
        assert len(set(ans)) == len(ans), '%s: верный вариант указан дважды' % where
        kind = q.get('kind', 'one')
        assert kind in ('one', 'many'), '%s: неизвестный тип %s' % (where, kind)
        if kind == 'one':
            assert len(ans) == 1, '%s: у вопроса с одним ответом их %d' % (where, len(ans))
        else:
            assert len(ans) > 1, '%s: помечен как «несколько», а верный один' % where
            assert len(ans) < len(opts), '%s: верны все варианты' % where

        assert q.get('why'), '%s: нет разбора' % where
        page = q['ref'][0]
        assert page in pages, '%s: ссылка на несуществующую страницу курса «%s»' % (where, page)
        if q.get('node'):
            node = q['node'][0]
            assert node in nodes, '%s: ссылка на несуществующий узел справочника «%s»' % (where, node)

    by_topic = {}
    for q in questions:
        by_topic[q['topic']] = by_topic.get(q['topic'], 0) + 1
    for t in data.TOPICS:
        assert by_topic.get(t['id']), 'тема «%s» осталась без вопросов' % t['id']


def payload(questions, nodes):
    out = []
    for q in questions:
        ans = q['answer']
        ans = ans if isinstance(ans, list) else [ans]
        links = [{'href': q['ref'][0] + '.html', 'label': 'Курс: ' + q['ref'][1]}]
        if q.get('node'):
            node = q['node']
            href = 'explorer.html#' + node[0] + ('/' + node[1] if len(node) > 1 else '')
            links.append({'href': href, 'label': 'Справочник: ' + nodes[node[0]]})
        # у «кодовых» вопросов вариант — дословная строка вывода, и разбор `кода`
        # съел бы в ней обратные кавычки имён из MySQL
        render = esc if q.get('mono') else inline
        item = {
            'id': q['id'],
            'topic': q['topic'],
            'kind': q.get('kind', 'one'),
            'text': inline(q['text']),
            'options': [render(o) for o in q['options']],
            'answer': ans,
            'why': inline(q['why']),
            'links': links,
        }
        if q.get('mono'):
            item['mono'] = True
        if q.get('code'):
            lang, code = q['code']
            item['code'] = ('<figure class="code"><div class="code-head">%s</div>'
                            '<pre><code>%s</code></pre></figure>'
                            % (esc(site.LANG_LABELS.get(lang, lang.upper())), site.highlight(code, lang)))
        out.append(item)
    return out


def build_page():
    css = open(os.path.join(SRC, 'quiz.css'), encoding='utf-8').read()
    js = open(os.path.join(SRC, 'quiz.js'), encoding='utf-8').read()

    nodes = explorer_topics()
    check(data.QUESTIONS, course_pages(), nodes)

    quiz = {
        'topics': [{'id': t['id'], 'title': t['title'], 'color': GROUP_COLOR[t['group']]}
                   for t in data.TOPICS],
        'questions': payload(data.QUESTIONS, nodes),
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
    <span class="mark"><b>Yii</b><span class="mark-text">Проверка знаний</span></span>
    <span class="top-count">%d %s · %d тем</span>
    <span class="top-spacer"></span>
    <a class="back-link" href="index.html">на главную</a>
    <button type="button" class="icon-btn" id="theme-btn" aria-label="Переключить тему">
      <svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
      <svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
</header>

<main class="stage">

  <section id="screen-start">
    <div class="hero">
      <p class="eyebrow">после курса и справочника</p>
      <h1>Проверка знаний</h1>
      <p>Вопрос, четыре варианта и разбор с ссылкой туда, где об этом написано подробно.
        Ответы к вопросам про код не сочинялись — каждый прогонялся на настоящем Yii&nbsp;2.</p>
    </div>

    <div class="modes">
      <button type="button" class="mode" id="mode-quick" style="--mc: var(--g-data)">
        <span class="mode-n">%d вопросов</span>
        <h2>Быстрый прогон</h2>
        <p>Случайная выборка по всем темам — размяться за пару минут.</p>
      </button>
      <button type="button" class="mode" id="mode-exam" style="--mc: var(--g-db)">
        <span class="mode-n">%d вопросов</span>
        <h2>Экзамен</h2>
        <p>Длинный набор вперемешку: видно, где знания просели.</p>
      </button>
      <button type="button" class="mode" id="mode-missed" style="--mc: var(--g-http)" disabled>
        <span class="mode-n">по вашим промахам</span>
        <h2>Работа над ошибками</h2>
        <p id="missed-note">Пока пусто — сначала пройдите любой набор</p>
      </button>
    </div>

    <h2 class="sec-h">Тренировка по теме</h2>
    <div class="topics" id="topics"></div>

    <div class="reset-row">
      <span id="seen-note"></span>
      <button type="button" class="linkish" id="reset">сбросить статистику</button>
    </div>
  </section>

  <section id="screen-run" class="run" hidden>
    <div class="runbar">
      <span class="rb-t" id="rb-title"></span>
      <span class="dots" id="dots"></span>
      <span class="rb-t" id="rb-pos"></span>
    </div>

    <div class="qbox" id="qbox">
      <div class="q-top">
        <span class="q-topic" id="q-topic"></span>
        <span class="q-kind" id="q-kind"></span>
      </div>
      <p class="q-text" id="q-text"></p>
      <div id="q-code" hidden></div>
      <div class="opts" id="opts"></div>

      <div class="verdict" id="verdict" hidden>
        <h3 id="v-head"></h3>
        <p id="v-why"></p>
        <div class="vlinks" id="v-links"></div>
      </div>

      <div class="acts">
        <button type="button" class="btn" id="act-main" disabled>Проверить</button>
        <button type="button" class="btn ghost" id="act-skip">Не знаю</button>
        <span class="kbd-hint">цифры — выбор, Enter — дальше</span>
      </div>
    </div>
  </section>

  <section id="screen-result" class="result" hidden>
    <div class="score">
      <span class="score-n" id="score-n"></span>
      <span class="score-side">
        <h2 id="score-h"></h2>
        <p id="score-p"></p>
      </span>
    </div>

    <h2 class="sec-h">По темам</h2>
    <div class="by-topic" id="by-topic"></div>

    <h2 class="sec-h" id="misses-h" hidden>Разобрать</h2>
    <div class="misses" id="misses"></div>

    <div class="acts">
      <button type="button" class="btn" id="again">Пройти ещё раз</button>
      <button type="button" class="btn ghost" id="again-missed" hidden>Только промахи</button>
      <button type="button" class="btn ghost" id="to-start">К выбору набора</button>
    </div>
  </section>

</main>

<script>
window.QUIZ=%s;
</script>
<script>
%s
</script>''' % (len(data.QUESTIONS), site.plural(len(data.QUESTIONS), 'вопрос', 'вопроса', 'вопросов'),
                len(data.TOPICS), 10, 40,
                json.dumps(quiz, ensure_ascii=False, separators=(',', ':')), js)

    return head, body


def main():
    head, body = build_page()
    size = catalog.write_page(OUT, FRAGMENT, TITLE, DESCRIPTION, head, body)
    print('Вопросов: %d, тем: %d, с кодом: %d'
          % (len(data.QUESTIONS), len(data.TOPICS),
             sum(1 for q in data.QUESTIONS if q.get('code'))))
    print('Готово: %s (%.0f КБ)' % (OUT, size / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
