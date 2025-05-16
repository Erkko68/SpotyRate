import { mediaState }    from './globals/mediaState.js';
import { initMediaClick }    from './handlers/mediaClick.js';
import { initSearchQuery }   from './handlers/searchQuery.js';
import { initNavigate }      from './handlers/navigate.js';
import { initStarRating }    from './handlers/starRating.js';
import { initCommentForm }   from './handlers/commentForm.js';
import { updateRightSidebar, hideCommentsSection, showCommentsSection  } from './comment_section.js';

document.addEventListener('DOMContentLoaded', () => {
  const mainContent = document.getElementById('main-content');

  initMediaClick(mainContent);
  initSearchQuery(mainContent, hideCommentsSection);
  initNavigate(mainContent, updateRightSidebar);
  initStarRating();
  initCommentForm(updateRightSidebar);
});
