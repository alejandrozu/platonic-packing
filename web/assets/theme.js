// Theme choice is shared by every page and remembered on this browser.
(() => {
  const key = 'ppr-theme', root = document.documentElement;
  const media = matchMedia('(prefers-color-scheme: dark)');
  const read = () => { try { const t = localStorage.getItem(key); return ['light', 'dark'].includes(t) ? t : null } catch (_) { return null } };
  function apply(theme, remember = false) {
    root.dataset.theme = theme;
    if (remember) { try { localStorage.setItem(key, theme) } catch (_) {} }
    document.querySelectorAll('.theme-switch button').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.theme === theme));
    });
    document.dispatchEvent(new CustomEvent('ppr-themechange', { detail: { theme } }));
  }
  function ready() {
    document.querySelectorAll('.theme-switch button').forEach(button => {
      button.addEventListener('click', () => apply(button.dataset.theme, true));
    });
    apply(read() || (media.matches ? 'dark' : 'light'));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();
  media.addEventListener('change', () => { if (!read()) apply(media.matches ? 'dark' : 'light') });
  addEventListener('storage', event => { if (event.key === key) apply(read() || (media.matches ? 'dark' : 'light')) });
})();
