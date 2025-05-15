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
        updateRightSidebar(id);
    });
});
