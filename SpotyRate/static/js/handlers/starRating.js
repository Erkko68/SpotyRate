export function initStarRating() {
  document.addEventListener('click', e => {
    const star = e.target.closest('.star');
    if (!star) return;

    const selectedValue = parseInt(star.dataset.value);
    updateStars(selectedValue);
  });
}

function updateStars(selectedValue) {
  const stars = document.querySelectorAll('.star');
  const starInput = document.getElementById('star-rating');

  stars.forEach(star => {
    const val = parseInt(star.dataset.value);
    const filled = val <= selectedValue;
    star.textContent = filled ? '★' : '☆';
    star.style.color = filled ? 'var(--color-spotify-green)' : 'gray';
  });

  starInput.value = selectedValue;
}
