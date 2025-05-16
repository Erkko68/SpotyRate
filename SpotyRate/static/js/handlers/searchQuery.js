import { fetchAndRender } from '../functions/fetchAndRender.js';

export function initSearchQuery(mainContent, hideCommentsSection) {
  document.addEventListener('searchQuery', e => {
    const { query } = e.detail;
    const url = `/search/?q=${encodeURIComponent(query)}`;

    hideCommentsSection();
    fetchAndRender(url, mainContent);
  });
}
