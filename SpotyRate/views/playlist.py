import requests
import logging
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def playlist_view(request):
    playlist_id = request.GET.get("id")
    access_token = request.session.get("spotify_access_token")

    # 1) Ensure we have a valid user token
    if not access_token:
        logger.error("User not authenticated")
        return JsonResponse({"error": "User not authenticated"}, status=401)

    # 2) Validate playlist_id
    if not playlist_id:
        logger.error("Playlist ID not provided")
        return JsonResponse({"error": "Playlist ID not provided"}, status=400)

    logger.debug(f"Fetching playlist {playlist_id}")

    playlist_data = {}

    # 3) Fetch playlist data from Spotify
    resp = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    logger.info(f"Spotify Playlist status: {resp.status_code}")

    try:
        payload = resp.json()
    except ValueError:
        logger.error("Spotify Playlist did not return JSON")
        payload = {}

    if resp.ok:
        # Extract relevant playlist data
        playlist_data = {
            "images": payload.get("images", []),
            "name": payload.get("name", "Unknown Playlist"),
            "owner": {
                "display_name": payload.get("owner", {}).get("display_name", "Unknown Creator")
            },
            "tracks": {
                "total": payload.get("tracks", {}).get("total", 0),
                "items": [
                    {
                        "added_at": item.get("added_at", "N/A"),
                        "track": {
                            "id": item["track"].get("id"),
                            "name": item["track"].get("name"),
                            "duration_ms": item["track"].get("duration_ms"),
                            "album": {
                                "name": item["track"].get("album", {}).get("name", "Unknown Album")
                            },
                            "artists": [
                                artist.get("name") for artist in item["track"].get("artists", [])
                            ]
                        }
                    }
                    for item in payload.get("tracks", {}).get("items", [])
                    if item.get("track")  # Ensure the track object is not None
                ]
            }
        }

        # Log the transformed data for debugging
        logger.debug(f"Processed Playlist Data: {playlist_data}")

    else:
        logger.error(f"Spotify Playlist error: {payload.get('error')}")

    # 4) Render the playlist template
    return render(request, "sections/playlist.html", {"playlist": playlist_data})
