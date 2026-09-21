<?php
/** Обычный режим: PHP приводит значение к объявленному типу, если может. */
require __DIR__ . '/probe.php';

$rows = [];
$diag = null;
probe_watch($diag);
foreach (probe_functions() as $type => $fn) {
    foreach (probe_values() as $label => $value) {
        $diag = null;
        try {
            $rows[$type][$label] = probe_ok($value, $fn($value), $diag);
        } catch (TypeError $e) {
            $rows[$type][$label] = probe_fail($e);
        }
    }
}
restore_error_handler();
echo json_encode($rows, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
