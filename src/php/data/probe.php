<?php
/**
 * Общая обвязка для двух замеров: обычного и строгого.
 *
 * Сам вызов `$fn($value)` живёт в probe-weak.php и probe-strict.php, а не здесь:
 * declare(strict_types=1) действует на файл, в котором стоит вызов, а не на тот,
 * где объявлена функция. Один общий цикл замерил бы оба раза обычный режим.
 */

require __DIR__ . '/common.php';

/** Ловит Deprecated/Warning, которые PHP выдаёт при приведении. */
function probe_watch(&$diag): void
{
    set_error_handler(function ($no, $msg) use (&$diag) {
        $kind = [E_DEPRECATED => 'Deprecated', E_WARNING => 'Warning'][$no] ?? 'Notice';
        $diag = $kind . ': ' . $msg;
        return true;
    });
}

/** Значение прошло: что от него осталось и с какой жалобой. */
function probe_ok($value, $got, ?string $diag): array
{
    $same = is_object($got) ? $got === $value : show($got) === show($value);
    return ['ok' => true, 'kept' => $same, 'got' => show($got), 'note' => $diag];
}

/** Значение не прошло: сообщение TypeError без имени служебного замыкания. */
function probe_fail(TypeError $e): array
{
    $msg = preg_replace('/^.*\(\): /', '', $e->getMessage());
    return ['ok' => false, 'kept' => false, 'got' => null,
            'note' => preg_replace('/, called in .*$/s', '', $msg)];
}
