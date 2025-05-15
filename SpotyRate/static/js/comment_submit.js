(() => {
  const form = document.getElementById('add-comment-form');
  if (!form) return console.error('Comment form not found');

  const commentField = form.querySelector('#comment-text');
  const starElems = Array.from(form.querySelectorAll('.stars .star'));
  const starInput = form.querySelector('#star-rating');
  const submitBtn = form.querySelector('button[type="submit"]');

  const mediaId = form.dataset.mediaId;
  const mediaType = form.dataset.mediaType;
  const commentsContainer = document.querySelector('.comments-list-container');
  const commentCountElem = document.querySelector('h2.text-2xl');

  // Helper to update star visuals and hidden input
  function setStars(value) {
    starInput.value = value;
    starElems.forEach((star, idx) => {
      const filled = idx < value;
      star.textContent = filled ? '★' : '☆';
      star.classList.toggle('text-[var(--color-spotify-green)]', filled);
      star.classList.toggle('text-gray-400', !filled);
    });
  }

  // Initialize stars
  setStars(0);
  starElems.forEach(star => {
    star.addEventListener('click', () => setStars(parseInt(star.dataset.value)));
  });

  // Submit handler
  form.addEventListener('submit', async event => {
    event.preventDefault();

    const comment = commentField.value.trim();
    const stars = parseInt(starInput.value);
    if (!comment) return alert('Please enter a comment.');
    if (!stars) return alert('Please provide a star rating.');

    // Disable inputs
    submitBtn.disabled = true;
    commentField.disabled = true;

    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const payload = {
      comment,
      stars,
      media_id: mediaId,
      media_type: mediaType
    };

    try {
      const response = await fetch('/api/comment/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || response.statusText);

      // Success: reset form
      commentField.value = '';
      setStars(0);

      // Append new comment
      if (data.html) {
        commentsContainer.querySelector('.empty-comments-message')?.remove();
        commentsContainer.insertAdjacentHTML('beforeend', data.html);
      }

      // Update count
      const currentCount = parseInt(commentCountElem.textContent) || 0;
      const nextCount = currentCount + 1;
      commentCountElem.textContent = `${nextCount}${nextCount === 1 ? ' Comment' : ' Comments'}`;

    } catch (error) {
      console.error('Comment submission error:', error);
      alert('Error: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      commentField.disabled = false;
    }
  });
})();