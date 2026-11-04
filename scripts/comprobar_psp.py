#!/usr/bin/env python3
"""Compila y comprueba por separado las dos implementaciones PSP."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(command, data=None, code=0):
    result = subprocess.run(command, input=data, text=True, encoding='utf-8',
                            capture_output=True, timeout=35)
    if result.returncode != code:
        raise RuntimeError('Fallo en ' + ' '.join(map(str, command)) + '\n' +
                           result.stdout + result.stderr)
    return result


def main():
    if not shutil.which('java') or not shutil.which('javac'):
        raise RuntimeError('Instala un JDK 17 o posterior con java y javac en PATH.')
    csv_path = ROOT / 'pruebas/fixtures/custom40.csv'
    data = csv_path.read_text(encoding='utf-8')
    csv_sources = [ROOT / 'psp' / (name + '.java') for name in
                   ('AnalizadorTallas', 'LanzadorValidacion', 'LectorCsv', 'ValidadorPedidoCustom')]
    packaged = sorted((ROOT / 'psp/src/Psp').glob('*.java'))
    if not all(p.is_file() for p in csv_sources) or not packaged:
        raise RuntimeError('Faltan fuentes PSP. Ejecuta esto desde la rama integrada.')
    with tempfile.TemporaryDirectory(prefix='nova-psp-') as folder:
        classes = Path(folder) / 'csv'
        other = Path(folder) / 'protocolo'
        classes.mkdir()
        other.mkdir()
        run(['javac', '-encoding', 'UTF-8', '-d', str(classes), *map(str, csv_sources)])
        java = ['java', '-Dfile.encoding=UTF-8', '-cp', str(classes)]
        response = run([*java, 'ValidadorPedidoCustom'], data)
        lines = response.stdout.splitlines()
        if not lines or lines[0].strip() != 'OK;CUSTOM-40;4;40':
            raise RuntimeError('El validador no reconoce los cuatro registros CSV multilínea.')
        normalized = [line for line in lines[1:] if line.startswith('LINEA;')]
        if len(normalized) != 4 or 'FIN' not in lines or 'PEDIDO;CUSTOM-40' not in lines:
            raise RuntimeError('El validador no devuelve los cuatro registros normalizados.')
        summary = run([*java, 'LanzadorValidacion', str(csv_path)]).stdout
        expected = [f'Talla {size}: 10 pares' for size in range(40, 44)] + ['Total: 40 pares']
        if not all(line in summary.splitlines() for line in expected):
            raise RuntimeError('El resumen del proceso padre no coincide con la muestra.')
        bad_samples = [data.replace(',40,10', ',40,0', 1),
                       data.replace('CUSTOM-40,DEMO-41', 'OTRO,DEMO-41', 1),
                       'referencia,sku\n"campo sin cierre']
        for sample in bad_samples:
            rejection = run([*java, 'ValidadorPedidoCustom'], sample, code=2)
            if not rejection.stderr.startswith('ERROR;'):
                raise RuntimeError('El rechazo no incluye el motivo por stderr.')
        run(['javac', '-encoding', 'UTF-8', '-d', str(other), *map(str, packaged)])
        output = run(['java', '-Dfile.encoding=UTF-8', '-cp', str(other),
                      'Psp.PruebasAnalizador']).stdout
        match = re.search(r'Pruebas superadas: (\d+) de (\d+)', output)
        if not match or int(match[1]) == 0 or match[1] != match[2] or '[FALLIDA]' in output:
            raise RuntimeError('Las pruebas del paquete Psp no se superaron:\n' + output)
    print('OK: CSV multilínea, resumen, tres rechazos y pruebas del paquete Psp.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
