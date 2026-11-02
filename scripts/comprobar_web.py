#!/usr/bin/env python3
"""Comprueba recursos locales HTML/CSS y las rutas de imágenes del catálogo."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('src', 'href', 'poster') and value:
                self.urls.append(value)


def main():
    base = ROOT / 'interfaces'
    htmls = sorted(base.rglob('*.html'))
    if not htmls:
        raise RuntimeError('No hay interfaces. Ejecuta esto desde la rama integrada.')
    errors = []
    checked = set()

    def check(source, url, relative_to=None):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return
        if parsed.path.startswith('/api/'):
            return
        parent = relative_to or source.parent
        target = (ROOT / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/')
                  else parent / unquote(parsed.path))
        target = target.resolve()
        checked.add(target)
        if not target.exists():
            errors.append(str(source.relative_to(ROOT)) + ': falta ' + url)

    for source in htmls:
        parser = References()
        parser.feed(source.read_text(encoding='utf-8'))
        for url in parser.urls:
            check(source, url)
    for source in base.rglob('*.css'):
        for match in re.finditer(r'url\(\s*[\'\"]?([^\)\'\"]+)[\'\"]?\s*\)',
                                 source.read_text(encoding='utf-8')):
            check(source, match[1].strip())
    catalog = base / 'cliente/js/modelos.js'
    if not catalog.is_file():
        errors.append('Falta interfaces/cliente/js/modelos.js')
    else:
        for url in re.findall(r'imagen(?:Catalogo)?\s*:\s*"([^"]+)"',
                              catalog.read_text(encoding='utf-8')):
            check(catalog, url, base / 'cliente')
    if errors:
        raise RuntimeError('\n'.join(sorted(set(errors))))
    print(f'OK: {len(htmls)} páginas HTML y {len(checked)} recursos locales distintos.')
    print('No se han comprobado servicios externos, API ni comportamiento visual.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
