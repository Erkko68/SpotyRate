import requests
import logging
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def search(request):
    query = request.GET.get("q", "").strip()
    access_token = request.session.get("spotify_access_token")

    # 1) Ensure we have a valid user token
    if not access_token:
        logger.error("User not authenticated")
        return JsonResponse({"error": "User not authenticated"}, status=401)

    logger.debug(f"Correct access token: {access_token}")

    tracks = albums = artists = playlists = []

    if query:
        # 2) Hit Spotify’s Search endpoint
        resp = requests.get(
            "https://api.spotify.com/v1/search",
            params={
                "q": query,
                "type": "track,album,artist,playlist",
                "limit": 10,
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # 3) Log status & JSON for debugging
        logger.info(f"Spotify Search status: {resp.status_code}")
        try:
            payload = resp.json()
            logger.debug(f"Spotify Search payload: {payload}")
        except ValueError:
            logger.error("Spotify Search did not return JSON")
            payload = {}

        # 4) On 200 OK, pull out each .items list
        if resp.ok:
            tracks    = [item for item in payload.get("tracks", {}).get("items", []) if item]
            albums    = [item for item in payload.get("albums", {}).get("items", []) if item]
            artists   = [item for item in payload.get("artists", {}).get("items", []) if item]
            playlists = [item for item in payload.get("playlists", {}).get("items", []) if item]

            logger.debug(f"Filtered Spotify Search Response OK: {resp}")
        else:
            logger.error(f"Spotify Search error: {payload.get('error')}")

    # 5) Render a search template using AJAX with search results
    return render(request, "sections/search.html", {
        "query": query,
        "results": {
            "tracks": tracks,
            "albums": albums,
            "artists": artists,
            "playlists": playlists,
        },
    })
