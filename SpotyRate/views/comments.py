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

    # Log comment count
    logger.info(f"Found {comment_count} comments for media ID {media_id}.")

    # Render the comments section, even if there are no comments
    html = render(request, 'sections/comments.html', {
        'comments': comments,
        'comment_count': comment_count,
    }).content.decode('utf-8')

    return JsonResponse({'html': html})


def submit_comment(request):
    """Handle comment submissions via AJAX form POST with hidden inputs for media ID/type"""
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    # Log raw POST data keys for debugging
    logger.debug(f"submit_comment POST keys: {list(request.POST.keys())}")
    logger.debug(f"All POST data: {request.POST}")

    try:
        # Extract everything from request.POST
        media_id   = request.POST.get('mediaId')
        media_type = request.POST.get('mediaType')
        stars_raw  = request.POST.get('stars')
        comment    = request.POST.get('comment', '').strip() or None

        logger.info(f"Parsed fields - mediaId: {media_id}, mediaType: {media_type}, stars: {stars_raw}, comment: {comment}")

        # Validate presence
        errors = []
        if not media_id:
            errors.append('mediaId is missing')
        if not media_type:
            errors.append('mediaType is missing')
        if not stars_raw:
            errors.append('stars is missing')

        # Convert stars
        try:
            stars = int(stars_raw)
        except (TypeError, ValueError):
            errors.append('stars must be an integer')
            stars = 0

        # If presence/parse errors, short-circuit
        if errors:
            err_msg = '; '.join(errors)
            logger.warning(f"Validation errors: {err_msg}")
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)

        # Domain validation
        if stars < 1 or stars > 5:
            raise ValidationError('Stars must be between 1 and 5')
        valid_types = dict(Media.MEDIA_TYPE_CHOICES)
        if media_type not in valid_types:
            raise ValidationError('Invalid media type')

        with transaction.atomic():
            media, created = Media.objects.get_or_create(
                spotify_media_id=media_id,
                defaults={'media_type': media_type}
            )
            if not created and media.media_type != media_type:
                media.media_type = media_type
                media.save(update_fields=['media_type'])

            rating = Rating.objects.create(
                user=request.user,
                media=media,
                stars=stars,
                comment=comment
            )

        comment_html = render_to_string(
            'sections/comments/_comment.html',
            {'rating': rating},
            request=request
        )
        logger.info(f"Successfully created rating {rating.id} for media {media_id}")
        return JsonResponse({
            'status': 'success',
            'html': comment_html,
            'new_media_created': created
        })

    except ValidationError as ve:
        logger.warning(f"ValidationError in submit_comment: {ve}")
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        logger.error(f"Comment submission error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)