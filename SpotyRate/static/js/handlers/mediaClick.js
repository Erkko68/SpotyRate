export function initMediaClick(mainContent) {
  mainContent.addEventListener('click', e => {
    const item = e.target.closest('.result-item');
    if (!item) return;

    const type = item.dataset.type;
    const id = item.dataset.id;
    console.log('Clicked:', type, id);
    document.dispatchEvent(new CustomEvent('navigate', {
      detail: { type, id }
    }));
  });
}
