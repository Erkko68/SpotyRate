import logging
from django.shortcuts import render
from django.http import JsonResponse
import requests

logger = logging.getLogger(__name__)

SPOTIFY_API_BASE = "https://api.spotify.com/v1"


class SpotifyAPIError(Exception):
    pass


def get_spotify_data(access_token: str, media_type: str, media_id: str) -> dict:
    """
    Fetches data from Spotify API for the given media type and ID.
    """
    endpoints = {
        'track': f"{SPOTIFY_API_BASE}/tracks/{media_id}",
        'playlist': f"{SPOTIFY_API_BASE}/playlists/{media_id}",
        'album': f"{SPOTIFY_API_BASE}/albums/{media_id}",
    }
    url = endpoints.get(media_type)
    if not url:
        raise ValueError(f"Unsupported media type: {media_type}")

    headers = {"Authorization": f"Bearer {access_token}"}
    logger.debug(f"Requesting Spotify {media_type}: {media_id}")
    resp = requests.get(url, headers=headers)

    try:
        data = resp.json()
    except ValueError:
        logger.error("Invalid JSON response from Spotify")
        raise SpotifyAPIError("Invalid JSON response from Spotify")

    if not resp.ok:
        error = data.get('error', {}).get('message', 'Unknown error')
        logger.error(f"Spotify API error ({resp.status_code}): {error}")
        raise SpotifyAPIError(error)

    return data


def normalize_playlist(payload: dict) -> dict:
    return {
        'type': 'playlist',
        'id': payload.get('id'),
        'name': payload.get('name'),
        'images': payload.get('images', []),
        'owner': {'display_name': payload.get('owner', {}).get('display_name')},
        'popularity': payload.get('popularity', 0),
        'tracks': {
            'total': payload.get('tracks', {}).get('total', 0),
            'items': [
                {
                    'added_at': item.get('added_at'),
                    'track': {
                        **item.get('track', {}),
                        'artists': [artist.get('name') for artist in item.get('track', {}).get('artists', [])]
                    }
                }
                for item in payload.get('tracks', {}).get('items', [])
                if item.get('track')
            ]
        }
    }


def normalize_track(payload: dict) -> dict:
    return {
        'type': 'track',
        'id': payload.get('id'),
        'name': payload.get('name'),
        'images': payload.get('album', {}).get('images', []),
        'duration_ms': payload.get('duration_ms'),
        'popularity': payload.get('popularity', 0),
        'artists': [{'name': artist.get('name')} for artist in payload.get('artists', [])],
        'album': payload.get('album', {}),
        'tracks': {
            'total': 1,
            'items': [
                {
                    'added_at': None,
                    'track': {
                        **payload,
                        'artists': [{'name': artist.get('name')} for artist in payload.get('artists', [])],
                        'album': payload.get('album', {})
                    }
                }
            ]
        }
    }


def normalize_album(payload: dict) -> dict:
    return {
        'type': 'album',
        'id': payload.get('id'),
        'name': payload.get('name'),
        'images': payload.get('images', []),
        'album_type': payload.get('album_type'),
        'release_date': payload.get('release_date'),
        'total_tracks': payload.get('total_tracks'),
        'popularity': payload.get('popularity', 0),
        'artists': [{'name': artist.get('name')} for artist in payload.get('artists', [])],
        'tracks': {
            'total': payload.get('tracks', {}).get('total', 0),
            'items': [
                {
                    'added_at': None,
                    'track': {
                        **track,
                        'artists': [{'name': a.get('name')} for a in track.get('artists', [])],
                    }
                }
                for track in payload.get('tracks', {}).get('items', [])
            ]
        }
    }


def media_view(request):
    media_id = request.GET.get('id')
    media_type = request.GET.get('type', 'track')  # Default to track
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        logger.error('User not authenticated')
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    if not media_id:
        logger.error('Media ID not provided')
        return JsonResponse({'error': 'Media ID not provided'}, status=400)

    try:
        payload = get_spotify_data(access_token, media_type, media_id)

        if media_type == 'playlist':
            media_data = normalize_playlist(payload)
        elif media_type == 'album':
            media_data = normalize_album(payload)
        else:
            media_data = normalize_track(payload)

    except SpotifyAPIError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'sections/media.html', {'media': media_data})
