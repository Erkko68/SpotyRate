from django.http import JsonResponse

import logging

logger = logging.getLogger(__name__)

def search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        logger.warning('Empty search query received')
        return JsonResponse({'error': 'Please enter a search term'}, status=400)

    logger.info(f"Search initiated for: {query}")
    print(f"Debug - Search query: {query}")

    # Process the search here later
    return JsonResponse({
        'query': query,
        'results': [
            {
                "name": "Song Name",
                "type": "song",
                "artist": "Artist Name"
            },
            {
                "name": "Playlist Name",
                "type": "playlist"
            }
        ]  # You'll populate this later
    })