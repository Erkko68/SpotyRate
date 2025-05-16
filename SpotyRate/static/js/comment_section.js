import { mediaState } from './globals/mediaState.js';

/**
 * Update the comments section based on a given media ID and media type.
 * If no mediaId is provided, the comments section will be hidden.
 * @param {string|null} mediaId - The media ID for which to update comments.
 * @param {string|null} mediaType - The media type for which to update comments.
 */
export async function updateRightSidebar(mediaId, mediaType) {
    const { html, userHasCommented } = await fetchComments(mediaId);
    showCommentsSection(html, mediaId, mediaType, userHasCommented);
}

/**
 * Hide the comments section and reset the layout.
 */
export function hideCommentsSection() {
    const sidebar = document.getElementById("right-sidebar");
    const mainContent = document.getElementById("main-content");

    sidebar.classList.add("hidden");
    mainContent.classList.remove("col-span-8");
    mainContent.classList.add("col-span-12");
}

/**
 * Show the comments section with the provided HTML content.
 * @param {string} html - The HTML content to display in the comments section.
 * @param {string} mediaId - The media ID to be set in the container.
 * @param {string} mediaType - The media type to be set in the container.
 * @param {boolean} userHasCommented - Whether the user has already commented.
 */
export function showCommentsSection(html, mediaId, mediaType, userHasCommented) {
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

    const removeButton = document.getElementById("remove-comment-btn");

    // Show/Hide the remove button
    if (removeButton) {
        removeButton.classList.toggle('hidden', !userHasCommented);
    }
}

/**
 * Fetch comments for a specific media ID via AJAX.
 * @param {string} mediaId - The media ID for which to fetch comments.
 * @returns {Promise<{html: string, userHasCommented: boolean}>} - The rendered HTML and user comment flag.
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
        return {
            html: data.html,
            userHasCommented: data.user_has_commented
        };
    } catch (error) {
        console.error('Error loading comments:', error);
        return {
            html: `
                <div class="p-4 text-center text-red-300">
                    Error loading comments. Please try again.
                </div>`,
            userHasCommented: false
        };
    }
}
