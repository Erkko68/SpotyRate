import requests
import logging
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def track_view(request):
    song_id = request.GET.get("id")
    access_token = request.session.get("spotify_access_token")

    # 1) Ensure we have a valid user token
    if not access_token:
        logger.error("User not authenticated")
        return JsonResponse({"error": "User not authenticated"}, status=401)

    # 2) Validate song_id
    if not song_id:
        logger.error("Song ID not provided")
        return JsonResponse({"error": "Song ID not provided"}, status=400)

    logger.debug(f"Fetching song {song_id}")

    song_data = {}

    # 3) Fetch song data from Spotify
    resp = requests.get(
        f"https://api.spotify.com/v1/tracks/{song_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    logger.info(f"Spotify Track status: {resp.status_code}")

    try:
        payload = resp.json()
    except ValueError:
        logger.error("Spotify Track did not return JSON")
        payload = {}

    if resp.ok:
        # Extract relevant song data
        song_data = {
            "id": payload.get("id"),
            "name": payload.get("name", "Unknown Song"),
            "duration_ms": payload.get("duration_ms", 0),
            "popularity": payload.get("popularity", 0),
            "added_at": "N/A",  # Placeholder as Spotify track data does not include "added_at"
            "preview_url": payload.get("preview_url", ""),
            "album": {
                "name": payload.get("album", {}).get("name", "Unknown Album"),
                "images": payload.get("album", {}).get("images", []),
            },
            "artists": [
                {"name": artist.get("name", "Unknown Artist")}
                for artist in payload.get("artists", [])
            ]
        }

        # Log the transformed data for debugging
        logger.debug(f"Processed Song Data: {song_data}")

    else:
        logger.error(f"Spotify Track error: {payload.get('error')}")

    # 4) Render the song template
    return render(request, "sections/song.html", {"song": song_data})
