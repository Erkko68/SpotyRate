import { fetchAndRender } from '../functions/fetchAndRender.js';
import { mediaState } from '../globals/mediaState.js';

export function initNavigate(mainContent, updateRightSidebar) {
  document.addEventListener('navigate', e => {
    const { type, id } = e.detail;
    const url = `/dashboard/media/?type=${encodeURIComponent(type)}&id=${encodeURIComponent(id)}`;

    mediaState.mediaId = id;
    mediaState.mediaType = type;
    document.querySelector('.media-container')
            ?.setAttribute('data-media-id', id);

    fetchAndRender(url, mainContent);
    updateRightSidebar(id, type);
  });
}
