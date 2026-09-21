<?php
/**
 * Считает таблицы для живых демонстраций справочника по PHP.
 *
 *     php src/php/data/gen.php
 *
 * Пишет рядом два файла, которые build_php.py вставляет в страницу:
 *     compare.json   что даёт сравнение и приведение пары значений
 *     types.json     что делает объявленный тип параметра в обоих режимах
 *
 * Считает это сам PHP, а не автор справочника: таблицы должны совпадать
 * с поведением языка, а не с представлением о нём.
 */

require __DIR__ . '/common.php';

/** Приведения и предикаты для одного значения. */
function cast_row($v): array
{
    $warn = null;
    set_error_handler(function ($no, $msg) use (&$warn) { $warn = $msg; return true; });
    $string = is_array($v) ? '«Array» + Warning' : var_export((string) $v, true);
    restore_error_handler();

    return [
        'type'    => get_debug_type($v),
        'bool'    => var_export((bool) $v, true),
        'int'     => is_array($v) ? '1 (непустой — 1, пустой — 0)' : var_export((int) $v, true),
        'float'   => is_array($v) ? '—' : var_export((float) $v, true),
        'string'  => $string,
        'empty'   => empty($v),
        'numeric' => is_string($v) ? is_numeric($v) : null,
        'warn'    => $warn,
    ];
}

$values = compare_values();
$labels = array_keys($values);

$compare = ['values' => [], 'eq' => [], 'id' => [], 'cmp' => []];
foreach ($labels as $label) {
    // ключ массива в PHP числовой, а подпись нужна строкой — иначе в JSON уедет число
    $compare['values'][] = ['label' => (string) $label] + cast_row($values[$label]);
}
foreach ($labels as $a) {
    $eq = $id = $cmp = [];
    foreach ($labels as $b) {
        $x = $values[$a];
        $y = $values[$b];
        $eq[] = ($x == $y) ? 1 : 0;
        $id[] = ($x === $y) ? 1 : 0;
        $cmp[] = $x <=> $y;
    }
    $compare['eq'][] = $eq;
    $compare['id'][] = $id;
    $compare['cmp'][] = $cmp;
}

$flags = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;
file_put_contents(__DIR__ . '/compare.json', json_encode($compare, $flags) . "\n");

$php = PHP_BINARY;
$types = [
    'types'  => probe_types(),
    'values' => array_keys(probe_values()),
    'weak'   => json_decode(shell_exec("$php " . escapeshellarg(__DIR__ . '/probe-weak.php')), true),
    'strict' => json_decode(shell_exec("$php " . escapeshellarg(__DIR__ . '/probe-strict.php')), true),
];
if (!$types['weak'] || !$types['strict']) {
    fwrite(STDERR, "не удалось получить результаты замеров\n");
    exit(1);
}
file_put_contents(__DIR__ . '/types.json', json_encode($types, $flags) . "\n");

printf("compare.json: %d значений, %d пар\ntypes.json: %d типов × %d значений × 2 режима\nPHP %s\n",
    count($labels), count($labels) ** 2, count($types['types']), count($types['values']), PHP_VERSION);
