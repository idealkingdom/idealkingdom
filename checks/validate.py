from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'docs'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.links, self.errors, self.scripts = [], set(), [], [], []
        self.current_json = None

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag not in VOID:
            self.stack.append(tag)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'a' and attrs.get('target') == '_blank':
            assert 'noopener' in attrs.get('rel', ''), 'Missing external link protection'
        if tag == 'img':
            assert 'alt' in attrs, 'Missing image alt'
        if tag == 'button':
            assert attrs.get('type') == 'button', 'Button has no explicit type'
            assert attrs.get('aria-label'), 'Theme button needs an accessible name'
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.current_json = ''

    def handle_endtag(self, tag):
        if tag not in VOID:
            if not self.stack or self.stack[-1] != tag:
                self.errors.append('Unbalanced closing tag: ' + tag)
            else:
                self.stack.pop()
        if tag == 'script' and self.current_json is not None:
            self.scripts.append(json.loads(self.current_json))
            self.current_json = None

    def handle_data(self, data):
        if self.current_json is not None:
            self.current_json += data

page = Page()
page.feed((ROOT / 'index.html').read_text())
assert not page.stack and not page.errors, (page.stack, page.errors)
for link in page.links:
    parsed = urlparse(link)
    if not parsed.scheme and not parsed.netloc:
        if parsed.path:
            assert (ROOT / unquote(parsed.path)).is_file(), 'Missing asset: ' + link
        if parsed.fragment:
            assert parsed.fragment in page.ids, 'Broken anchor: ' + link
assert page.scripts[0]['name'] == 'Jeff Eric Cabarrubias'
ET.parse(ROOT / 'assets/favicon.svg')
assert (ROOT / 'assets/Jeff_Eric_Cabarrubias_Resume.pdf').read_bytes().startswith(b'%PDF-')
assert (ROOT / 'assets/social.png').is_file()

css = (ROOT / 'styles.css').read_text()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
depth = 0
for char in css:
    depth += (char == '{') - (char == '}')
    assert depth >= 0, 'Unexpected CSS brace'
assert depth == 0, 'Unbalanced CSS braces'
for requirement in ('prefers-reduced-motion', ':focus-visible', '[data-theme="dark"]', '@media(max-width:420px)', '.skip-link'):
    assert requirement in css, 'Missing responsive/accessibility rule: ' + requirement
print(f'PASS: HTML structure, {len(page.ids)} unique IDs, {len(page.links)} link/asset references, metadata, resume, favicon, CSS structure.')
