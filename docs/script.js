'use strict';

(() => {
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const color = document.querySelector('meta[name="theme-color"]');

  function setTheme(theme) {
    const dark = theme === 'dark';
    root.dataset.theme = dark ? 'dark' : 'light';
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    color.content = dark ? '#141619' : '#ffffff';
  }

  setTheme(root.dataset.theme);
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    try { localStorage.setItem('jeff-portfolio-theme', next); } catch (_) {}
  });

  document.getElementById('year').textContent = new Date().getFullYear();
})();
