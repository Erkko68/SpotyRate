import json
import logging
import requests

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from ..models import Media, Rating

logger = logging.getLogger(__name__)

def media_comments(request):
    """
    AJAX view to fetch comments for a specific media (song, playlist, album)
    and embed RDFa metadata for semantic web.
    """
    logger.debug("Triggered comments fetch.")

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.warning("Invalid request type received.")
        return HttpResponseBadRequest("Invalid request type.")

    media_id = request.GET.get('id')
    if not media_id:
        logger.warning("Missing media ID parameter in request.")
        return HttpResponseBadRequest("Missing media ID parameter.")

    # Attempt to fetch the Media object
    try:
        media = Media.objects.get(spotify_media_id=media_id)
        logger.info(f"Fetched media object for ID {media_id}: {media}")
    except Media.DoesNotExist:
        logger.warning(f"No media found for ID {media_id}. Returning empty comment section.")
        html = render(request, 'sections/comments.html', {
            'comments': [],
            'comment_count': 0,
        }).content.decode('utf-8')
        return JsonResponse({
            'html': html,
            'user_has_commented': False
        })

    # Spotify API request
    access_token = request.session.get("spotify_access_token")
    if not access_token:
        logger.error("Spotify access token not found in session.")
        return HttpResponseBadRequest("Spotify access token missing.")

    headers = {"Authorization": f"Bearer {access_token}"}
    api_url = f"https://api.spotify.com/v1/{media.media_type}s/{media.spotify_media_id}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch media metadata from Spotify: {e}")
        return HttpResponseBadRequest("Error fetching metadata from Spotify.")

    # Construct RDFa metadata
    item_reviewed_props = {
        "type": "MusicRecording" if media.media_type == "track" else
                "MusicAlbum" if media.media_type == "album" else
                "MusicPlaylist",
        "name": data.get("name"),
        "url": data.get("external_urls", {}).get("spotify"),
        "artist_names": [],
        "artist_property": "byArtist",
        "album_name": None,
        "album_url": None,
        "release_date": None,
        "duration": None,
    }

    if media.media_type == "track":
        item_reviewed_props["artist_names"] = [artist["name"] for artist in data.get("artists", [])]
        item_reviewed_props["album_name"] = data.get("album", {}).get("name")
        item_reviewed_props["album_url"] = data.get("album", {}).get("external_urls", {}).get("spotify")
        item_reviewed_props["release_date"] = data.get("album", {}).get("release_date")
        item_reviewed_props["duration"] = data.get("duration_ms") // 1000 if data.get("duration_ms") else None

    elif media.media_type == "album":
        item_reviewed_props["artist_names"] = [artist["name"] for artist in data.get("artists", [])]
        item_reviewed_props["release_date"] = data.get("release_date")

    elif media.media_type == "playlist":
        owner = data.get("owner", {}).get("display_name")
        if owner:
            item_reviewed_props["artist_names"] = [owner]
            item_reviewed_props["artist_property"] = "creator"

    # Fetch comments
    comments = Rating.objects.filter(media=media).select_related('user').order_by('-created_at')
    comment_count = comments.count()
    user_has_commented = comments.filter(user=request.user).exists()

    html = render(request, 'sections/comments.html', {
        'comments': comments,
        'comment_count': comment_count,
        'media': media,
        'item_reviewed_props': item_reviewed_props,
    }).content.decode('utf-8')

    return JsonResponse({
        'html': html,
        'user_has_commented': user_has_commented
    })

def submit_comment(request):
    """Handle comment submissions or updates via AJAX POST."""
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        logger.warning("Invalid request method or missing AJAX header.")
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    logger.debug(f"Received POST data: {request.POST}")

    try:
        # Extract and validate input data
        media_id = request.POST.get('mediaId')
        media_type = request.POST.get('mediaType')
        stars_raw = request.POST.get('stars')
        comment = request.POST.get('comment', '').strip() or None

        logger.info(f"Parsed fields - mediaId: {media_id}, mediaType: {media_type}, stars: {stars_raw}, comment: {comment}")

        # Validate presence
        errors = []
        if not media_id:
            errors.append('mediaId is missing')
        if not media_type:
            errors.append('mediaType is missing')
        if not stars_raw:
            errors.append('stars is missing')

        # Validate stars
        try:
            stars = int(stars_raw)
            if stars < 1 or stars > 5:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('stars must be an integer between 1 and 5')

        # Validate media type
        valid_types = dict(Media.MEDIA_TYPE_CHOICES)
        if media_type not in valid_types:
            errors.append('Invalid media type')

        if errors:
            error_message = '; '.join(errors)
            logger.warning(f"Validation errors: {error_message}")
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)

        # Proceed with creating or updating the rating
        with transaction.atomic():
            # Get or create media
            media, created = Media.objects.get_or_create(
                spotify_media_id=media_id,
                defaults={'media_type': media_type}
            )

            # If media already exists, ensure the media type is up-to-date
            if not created and media.media_type != media_type:
                media.media_type = media_type
                media.save(update_fields=['media_type'])
                logger.info(f"Updated media type for {media_id} to {media_type}")

            # Check if the user already has a rating for this media
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                media=media,
                defaults={
                    'stars': stars,
                    'comment': comment
                }
            )

            action = "created" if created else "updated"
            logger.info(f"Successfully {action} rating {rating.id} for media {media_id}")

        # Render the updated comment
        comment_html = render_to_string(
            'sections/comments/_comment.html',
            {'rating': rating},
            request=request
        )

        return JsonResponse({
            'status': 'success',
            'html': comment_html,
            'new_media_created': created,
            'action': action
        })

    except ValidationError as ve:
        logger.warning(f"ValidationError: {ve}")
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        logger.exception("Exception in submit_comment")
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

def remove_comment(request):
    # Only allow AJAX
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    try:
        payload = json.loads(request.body or "{}")
        media_id = payload.get('mediaId')
        media_type = payload.get('mediaType')

        if not media_id or not media_type:
            return JsonResponse({'status': 'error', 'message': 'Missing mediaId or mediaType'}, status=400)

        with transaction.atomic():
            # Try to find the media; if missing, treat as “already gone”
            media = Media.objects.filter(spotify_media_id=media_id).first()
            if not media:
                # nothing to delete
                return JsonResponse({'status': 'success'})

            # Try to delete the user’s rating; ignore if it doesn’t exist
            Rating.objects.filter(user=request.user, media=media).delete()

            # Optionally clean up orphaned media
            if not Rating.objects.filter(media=media).exists():
                media.delete()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.exception("Error in delete_comment")
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)
