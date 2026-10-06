const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../docs/script.js'), 'utf8');
for (const initial of ['light', 'dark']) {
  for (const storageThrows of [false, true]) {
    const listeners = {};
    const attributes = {};
    const root = { dataset: { theme: initial } };
    const toggle = { hidden: true, setAttribute(k, v) { attributes[k] = v; }, addEventListener(k, f) { listeners[k] = f; } };
    const color = { content: '' };
    const year = { textContent: '' };
    const saved = {};
    const context = { Date, document: { documentElement: root, getElementById(id) { return id === 'year' ? year : toggle; }, querySelector() { return color; } }, localStorage: { setItem(k, v) { if (storageThrows) throw new Error('Storage unavailable'); saved[k] = v; } } };
    vm.runInNewContext(source, context);
    assert.equal(toggle.hidden, false);
    assert.equal(attributes['aria-pressed'], String(initial === 'dark'));
    listeners.click();
    const next = initial === 'dark' ? 'light' : 'dark';
    assert.equal(root.dataset.theme, next);
    assert.equal(attributes['aria-pressed'], String(next === 'dark'));
    assert.equal(attributes['aria-label'], `Switch to ${next === 'dark' ? 'light' : 'dark'} mode`);
    assert.equal(color.content, next === 'dark' ? '#141619' : '#ffffff');
    if (!storageThrows) assert.equal(saved['jeff-portfolio-theme'], next);
    listeners.click();
    assert.equal(root.dataset.theme, initial);
    assert.equal(year.textContent, new Date().getFullYear());
  }
}
console.log('PASS: theme toggle, accessible state, persistence, blocked storage, and year.');
