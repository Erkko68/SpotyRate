from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import SpotifyUserManager

class SpotifyUser(AbstractBaseUser, PermissionsMixin):
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = SpotifyUserManager()

    USERNAME_FIELD = 'spotify_id'

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('track', 'Track'),
        ('playlist', 'Playlist'),
        ('album', 'Album')
    )

    spotify_media_id = models.CharField(max_length=100, unique=True)  # Unique Spotify media ID
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    def __str__(self):
        return f"Media(id={self.spotify_media_id}, type={self.media_type})"


class Rating(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='ratings')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='ratings')
    stars = models.IntegerField()  # The star rating given by the user
    comment = models.CharField(max_length=512, blank=True, null=True)  # Optional user comment
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'media'], name='unique_user_media_rating')
        ]

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Rating(user='{self.user.display_name}', "
            f"stars={self.stars}, "
            f"comment='{self.comment[:20] + '...' if self.comment and len(self.comment) > 20 else self.comment or 'None'}', "
            f"created_at={self.created_at.date() if self.created_at else 'N/A'}, "
            f"media_id={self.media.spotify_media_id}, "
            f"media_type={self.media.media_type})"
        )