import { mediaState } from '../globals/mediaState.js';
import { getCookie } from '../functions/getCookie.js';

export function initCommentForm(updateRightSidebar) {
  document.addEventListener('submit', async e => {
    const form = document.getElementById('comment-form');
    if (!form || e.target !== form) return;

    e.preventDefault();
    console.log("Form submission with global state:", mediaState);

    const formData = new FormData(form);
    formData.append('mediaId', mediaState.mediaId);
    formData.append('mediaType', mediaState.mediaType);

    for (let [k, v] of formData.entries()) {
      console.log(`  ${k}:`, v);
    }

    try {
      const url = `/api/comment/submit/`;
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData,
      });
      if (!res.ok) throw new Error(`Error: ${res.status}`);

      await res.text(); // discard
      updateRightSidebar(mediaState.mediaId, mediaState.mediaType);

      form.reset();
      document.getElementById('star-rating').value = "0";
      form.querySelectorAll('.star').forEach(star => {
        star.classList.remove('text-yellow-500');
        star.classList.add('text-gray-400');
      });
    } catch (err) {
      console.error('Comment submission error:', err);
    }
  });
}
