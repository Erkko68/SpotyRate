import json
import logging

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
    AJAX view to fetch comments for a specific media (song, playlist, album).
    """
    logger.debug("Triggered comments fetch.")

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.warning("Invalid request type received.")
        return HttpResponseBadRequest("Invalid request type.")

    media_id = request.GET.get('id')
    if not media_id:
        logger.warning("Missing media ID parameter in request.")
        return HttpResponseBadRequest("Missing media ID parameter.")

    # Fetch the media object
    logger.debug(f"Requested media with id {media_id}.")
    try:
        media = Media.objects.get(spotify_media_id=media_id)
        logger.info(f"Fetched media object for ID {media_id}: {media}")
    except Media.DoesNotExist:
        logger.warning(f"No media found for ID {media_id}. Returning empty comment section.")
        media = None

    # Fetch related ratings (comments) ordered by creation date (latest first)
    comments = Rating.objects.filter(media=media).select_related('user').order_by('-created_at') if media else []
    comment_count = comments.count() if media else 0

    # Check if the current user has already commented
    user_has_commented = comments.filter(user=request.user).exists() if media else False

    # Log comment count and user comment existence
    logger.info(f"Found {comment_count} comments for media ID {media_id}. User has commented: {user_has_commented}")

    # Render the comments section, even if there are no comments
    html = render(request, 'sections/comments.html', {
        'comments': comments,
        'comment_count': comment_count,
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
