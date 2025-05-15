/**
 * Update the comments section based on a given media ID and media type.
 * If no mediaId is provided, the comments section will be hidden.
 * @param {string|null} mediaId - The media ID for which to update comments.
 * @param {string|null} mediaType - The media type for which to update comments.
 */
async function updateRightSidebar(mediaId, mediaType) {
    const html = await fetchComments(mediaId);
    showCommentsSection(html, mediaId, mediaType);
}


/**
 * Hide the comments section and reset the layout.
 */
function hideCommentsSection() {
    const sidebar = document.getElementById("right-sidebar");
    const mainContent = document.getElementById("main-content");

    sidebar.classList.add("hidden");
    mainContent.classList.remove("col-span-8");
    mainContent.classList.add("col-span-12");
}

/**
 * Fetch comments for a specific media ID via AJAX.
 * @param {string} mediaId - The media ID for which to fetch comments.
 * @returns {Promise<string>} - The rendered HTML from the server.
 */
async function fetchComments(mediaId) {
    const url = `/api/comment/fetch/?id=${encodeURIComponent(mediaId)}`;
    console.log("Fetching comments from:", url);

    try {
        const response = await fetch(url, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });

        if (!response.ok) {
            console.error(`Error: Received status ${response.status}`);
            throw new Error('Failed to fetch comments');
        }

        const data = await response.json();
        return data.html;
    } catch (error) {
        console.error('Error loading comments:', error);
        return `
            <div class="p-4 text-center text-red-300">
                Error loading comments. Please try again.
            </div>`;
    }
}


/**
 * Show the comments section with the provided HTML content.
 * @param {string} html - The HTML content to display in the comments section.
 * @param {string} mediaId - The media ID to be set in the container.
 * @param {string} mediaType - The media type to be set in the container.
 */
function showCommentsSection(html, mediaId, mediaType) {
    const sidebar = document.getElementById("right-sidebar");
    const mainContent = document.getElementById("main-content");

    sidebar.innerHTML = html;
    sidebar.classList.remove("hidden");
    mainContent.classList.remove("col-span-12");
    mainContent.classList.add("col-span-8");

    // Update global state
    mediaState.mediaId = mediaId;
    mediaState.mediaType = mediaType;

    console.log("Global state updated:", mediaState);
}