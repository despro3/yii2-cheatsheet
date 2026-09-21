# -*- coding: utf-8 -*-
"""Содержимое «Справочника PHP 8+»: сборка узлов из sec_*.py и их порядок.

Узлы описаны по файлам-семействам, здесь они складываются в один список
и выстраиваются в том порядке, в котором идут по схеме — слева направо
и сверху вниз. Из этого же порядка берётся сквозная нумерация.
"""

from model import GROUPS, TOPICS          # noqa: F401  GROUPS уходит в сборку как есть

import sec_exec                           # noqa: F401,E402  путь кода
import sec_val                            # noqa: F401,E402  значения
import sec_fn                             # noqa: F401,E402  функции
import sec_oop                            # noqa: F401,E402  объекты
import sec_lib                            # noqa: F401,E402  стандартная библиотека
import sec_eco                            # noqa: F401,E402  вокруг языка

from sec_eco import VERSIONS              # noqa: F401,E402  данные для демонстрации версий

# порядок узлов задаётся явно — так они стоят на схеме
ORDER = [
    'runtime', 'autoload', 'errors',
    'types', 'operators', 'strings', 'arrays',
    'functions', 'closures', 'generators', 'fibers',
    'classes', 'props', 'interfaces', 'traits', 'enums', 'magic',
    'datetime', 'json', 'regex', 'files', 'spl',
    'attributes', 'composer', 'psr', 'tools', 'versions',
]

_known = {t['id'] for t in TOPICS}
assert _known == set(ORDER), 'ORDER и TOPICS разошлись: %s' % (_known ^ set(ORDER))
assert len(ORDER) == len(set(ORDER)), 'в ORDER есть повторы'
TOPICS.sort(key=lambda t: ORDER.index(t['id']))

# группы в ORDER должны идти подряд и в том же порядке, что и в GROUPS,
# иначе сквозная нумерация разойдётся с порядком карточек на странице
_gseq = [t['group'] for t in TOPICS]
_gidx = [g for g, _, _ in GROUPS].index
assert _gseq == sorted(_gseq, key=_gidx), 'группы в ORDER идут вразнобой: %s' % _gseq

# у каждого узла три вкладки с одинаковыми идентификаторами
for _t in TOPICS:
    assert [x[0] for x in _t['tabs']] == ['how', 'all', 'own'], \
        'у узла %s другие вкладки: %s' % (_t['id'], [x[0] for x in _t['tabs']])
