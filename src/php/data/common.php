<?php
/**
 * Общие списки для генераторов таблиц справочника.
 *
 * Значения перечислены так, чтобы в таблице сравнения встретились все
 * интересные случаи: числовые и нечисловые строки, ведущий ноль,
 * экспоненциальная запись, пустая строка и пробел, null, булевы, массив.
 */

/** Значения для таблицы сравнения: подпись => выражение. */
function compare_values(): array
{
    return [
        '0'      => 0,
        '1'      => 1,
        '-1'     => -1,
        '0.0'    => 0.0,
        "'0'"    => '0',
        "'1'"    => '1',
        "'01'"   => '01',
        "'1e1'"  => '1e1',
        "''"     => '',
        "' '"    => ' ',
        "'abc'"  => 'abc',
        "'0abc'" => '0abc',
        'null'   => null,
        'true'   => true,
        'false'  => false,
        '[]'     => [],
    ];
}

/** Объявления типов для таблицы проверки: подпись => код типа. */
function probe_types(): array
{
    return ['int', '?int', 'float', 'string', 'bool', 'array', 'iterable',
            'callable', 'object', 'mixed', 'int|string', 'int|false',
            'Stringable', 'Countable&ArrayAccess'];
}

/** Значения, которые пробуем передать в параметр с объявленным типом. */
function probe_values(): array
{
    return [
        '42'                    => 42,
        '3.14'                  => 3.14,
        '3.0'                   => 3.0,
        "'42'"                  => '42',
        "'42abc'"               => '42abc',
        "'abc'"                 => 'abc',
        "''"                    => '',
        'true'                  => true,
        'null'                  => null,
        '[1, 2]'                => [1, 2],
        "new ArrayObject([1])"  => new ArrayObject([1]),
        "'strlen'"              => 'strlen',
    ];
}

/** Короткая запись значения так, как его напечатал бы var_export. */
function show($v): string
{
    if (is_object($v)) {
        return get_class($v);
    }
    if (is_array($v)) {
        return $v === [] ? '[]' : '[' . implode(', ', array_map('show', $v)) . ']';
    }
    if (is_float($v)) {
        $s = var_export($v, true);
        return $s;
    }
    return var_export($v, true);
}

/** Функции с объявленным типом параметра: тип => замыкание. */
function probe_functions(): array
{
    $out = [];
    foreach (probe_types() as $type) {
        $out[$type] = eval("return function ($type \$x) { return \$x; };");
    }
    return $out;
}
