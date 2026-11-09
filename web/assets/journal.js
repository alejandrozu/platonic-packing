/* Progressive enhancement: the complete catalogue remains readable without JS. */
(() => {
  const search = document.getElementById('journal-search');
  const group = document.getElementById('journal-group');
  if (!search || !group) return;
  const cards = [...document.querySelectorAll('[data-journal-card]')];
  const sections = [...document.querySelectorAll('[data-journal-group]')];
  const count = document.getElementById('journal-results');
  const empty = document.getElementById('journal-empty');
  function filter() {
    const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = (group.value === 'all' || card.dataset.group === group.value) &&
        words.every(word => card.dataset.search.includes(word));
      card.hidden = !matches;
      if (matches) visible += 1;
    }
    for (const section of sections) section.hidden = ![...section.querySelectorAll('[data-journal-card]')].some(card => !card.hidden);
    count.textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'}`;
    empty.hidden = visible !== 0;
  }
  search.addEventListener('input', filter);
  group.addEventListener('change', filter);
})();
