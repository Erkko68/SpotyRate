import { mediaState } from '../globals/mediaState.js';
import { getCookie } from '../functions/getCookie.js';

export function initRemoveComment(updateRightSidebar) {
  document.addEventListener('click', async e => {
    if (!e.target.matches('.remove-comment-btn')) return;

    // Confirm with the user
    if (!confirm('Are you sure you want to remove your rating?')) return;

    // Grab mediaId + mediaType from nearest wrapper (or from mediaState)
    const container = e.target.closest('.comment');
    const mediaId   = container?.dataset.mediaId   ?? mediaState.mediaId;
    const mediaType = container?.dataset.mediaType ?? mediaState.mediaType;

    try {
      const res = await fetch(`/api/comment/delete/`, {
        method: 'POST',                         // easier with Django CSRF
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ mediaId, mediaType }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.status !== 'success') throw new Error(data.message);

      // Remove the comment from the DOM (or re-render sidebar)
      updateRightSidebar(mediaId, mediaType);
    } catch (err) {
      console.error('Failed to delete comment:', err);
      alert('Could not remove your rating. Please try again.');
    }
  });
}
