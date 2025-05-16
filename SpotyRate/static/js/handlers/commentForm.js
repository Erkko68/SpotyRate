import { mediaState } from '../globals/mediaState.js';
import { getCookie } from '../functions/getCookie.js';

export function initCommentForm(updateRightSidebar) {
  document.addEventListener('submit', async e => {
    const form = document.getElementById('comment-form');
    if (!form || e.target !== form) return;

    e.preventDefault();
    console.log("Form submission with global state:", mediaState);

    const formData = new FormData(form);

    const stars = formData.get('stars');
    if (!stars || stars === "0") {
      displayError(form,"Please select stars.");
      return;
    }

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

      if (!res.ok) {
        const errorText = await res.text();
        console.warn(`Error response: ${errorText}`);
        throw new Error(`Error: ${res.status}`);
      }

      await res.text(); // discard
      updateRightSidebar(mediaState.mediaId, mediaState.mediaType);

      form.reset();
      resetStars(form);
      clearError(form);

    } catch (err) {
      console.error('Comment submission error:', err);
      displayError('Failed to submit comment. Please try again.');
    }
  });

  function resetStars(form) {
    document.getElementById('star-rating').value = "0";
    form.querySelectorAll('.star').forEach(star => {
      star.classList.remove('text-yellow-500');
      star.classList.add('text-gray-400');
    });
  }

  function displayError(form, message) {
    const errorElement = form.querySelector('.error-message');
    if (!errorElement) return;
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
  }

  function clearError(form) {
    const errorElement = form.querySelector('.error-message');
    if (!errorElement) return;
    errorElement.textContent = '';
    errorElement.classList.add('hidden');
  }
}
