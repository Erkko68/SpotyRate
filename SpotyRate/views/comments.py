import json
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

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
    html = render(request, 'sections/comment_section.html', {
        'comments': comments,
        'comment_count': comment_count,
    }).content.decode('utf-8')

    return JsonResponse({'html': html})

def submit_comment(request):
    """Handle comment submissions with media creation/update logic"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    try:
        with transaction.atomic():
            data = json.loads(request.body)
            media_id = data['media_id']
            media_type = data['media_type']
            stars = int(data['stars'])
            comment = data.get('comment', '').strip() or None

            # Validate input
            if not 1 <= stars <= 5:
                raise ValidationError('Stars must be between 1-5')
            if media_type not in dict(Media.MEDIA_TYPE_CHOICES):
                raise ValidationError('Invalid media type')

            # Get or create media
            media, created = Media.objects.get_or_create(
                spotify_media_id=media_id,
                defaults={'media_type': media_type}
            )

            # Update media type if changed
            if not created and media.media_type != media_type:
                media.media_type = media_type
                media.save(update_fields=['media_type'])

            # Create rating
            rating = Rating.objects.create(
                user=request.user.spotifyuser,
                media=media,
                stars=stars,
                comment=comment
            )

            return JsonResponse({
                'status': 'success',
                'html': render_to_string('comments/comment_item.html', {'rating': rating}),
                'new_media_created': created
            })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e}'}, status=400)
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Comment submission error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)