const mediaState = {
    mediaId: null,
    mediaType: null,
};

document.addEventListener('DOMContentLoaded', () => {
    const mainContent = document.getElementById('main-content');

    /**
     * Handle click events on media items.
     */
    mainContent.addEventListener('click', function (e) {
        const item = e.target.closest('.result-item');
        if (!item) return;

        const type = item.dataset.type;
        const id = item.dataset.id;

        console.log('Clicked:', type, id);
        document.dispatchEvent(new CustomEvent('navigate', {
            detail: { type, id }
        }));
    });

    /**
     * Fetch and render the main content based on the provided URL.
     * @param {string} url - The URL to fetch content from.
     */
    async function fetchAndRender(url) {
        try {
            const res = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!res.ok) throw new Error(res.status);
            const html = await res.text();
            mainContent.innerHTML = html;
        } catch (err) {
            console.error('Fetch error:', err);
            mainContent.innerHTML = `
                <div class="p-4 text-center text-red-300">
                    Something went wrong. Please try again.
                </div>`;
        }
    }

    /**
     * Handle the search query event.
     * Hide the comments section and fetch search results.
     */
    document.addEventListener('searchQuery', e => {
        const { query } = e.detail;
        const url = `/search/?q=${encodeURIComponent(query)}`;
        hideCommentsSection(); // Hide comments when a search is initiated
        fetchAndRender(url);
    });

    /**
     * Handle the navigated event.
     * Fetch main content and comments based on the media ID.
     */
    document.addEventListener('navigate', async e => {
        const { type, id } = e.detail;
        const url = `/dashboard/media/?type=${encodeURIComponent(type)}&id=${encodeURIComponent(id)}`;

        // Store media ID in the container
        document.querySelector('.media-container')?.setAttribute('data-media-id', id);

        // Fetch main content and comments concurrently
        fetchAndRender(url);
        updateRightSidebar(id, type);
    });

    /**
     * Stars click handler
     */
    document.addEventListener('click', (e) => {
        const star = e.target.closest('.star');
        if (!star) return;

        const selectedValue = parseInt(star.dataset.value);
        updateStars(selectedValue);
    });

    function updateStars(selectedValue) {
        const starElems = document.querySelectorAll('.star');
        const starInput = document.getElementById('star-rating');

        starElems.forEach(star => {
            const starValue = parseInt(star.dataset.value);
            const isFilled = starValue <= selectedValue;

            star.textContent = isFilled ? '★' : '☆';
            star.style.color = isFilled ? 'var(--color-spotify-green)' : 'gray';
        });

        starInput.value = selectedValue;
    }

    document.addEventListener('submit', async (e) => {
        const form = document.getElementById("comment-form");
        if (!form || e.target !== form) return;

        e.preventDefault();

        // Pull from global state
        const {mediaId, mediaType} = mediaState;
        console.log("Form submission with global state:", {mediaId, mediaType});

        // Build FormData and include global values
        const formData = new FormData(form);
        formData.append('mediaId', mediaId);
        formData.append('mediaType', mediaType);

        // Optional: log FormData entries
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}:`, value);
        }

        try {
            const url = `/api/comment/submit/`;
            const csrfToken = getCookie('csrftoken');
            const res = await fetch(url, {
                method: 'POST',
                credentials: 'same-origin',            // include cookies on same-origin
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,            // Django’s default header name
                },
                body: formData,
            });

            if (!res.ok) throw new Error(`Error: ${res.status}`);

            const html = await res.text();
            updateRightSidebar(mediaId, mediaType);

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

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

});
