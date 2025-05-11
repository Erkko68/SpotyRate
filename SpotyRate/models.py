from django.db import models
from django.core.exceptions import ValidationError


class SpotifyUser(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)  # Unique Spotify user ID
    display_name = models.CharField(max_length=255)  # Spotify display name
    email = models.EmailField(blank=True, null=True)  # Optional email address
    profile_image_url = models.URLField(blank=True, null=True)  # Optional profile image URL

    def __str__(self):
        return (
            f"SpotifyUser("
            f"id={self.spotify_id}, "
            f"name='{self.display_name}', "
            f"email='{self.email}', "
            f")"
        )


class Song(models.Model):
    spotify_song_id = models.CharField(max_length=100, unique=True)  # Unique Spotify song ID

    # Optional: Add more fields like title, artist, etc. if needed

    def __str__(self):
        return f"Song(id={self.spotify_song_id})"


class Playlist(models.Model):
    spotify_playlist_id = models.CharField(max_length=100, unique=True)  # Unique Spotify playlist ID

    # Optional: Add more fields like name, owner, etc. if needed

    def __str__(self):
        return f"Playlist(id={self.spotify_playlist_id})"


class Rating(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='ratings')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, blank=True, null=True, related_name='ratings')
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, blank=True, null=True, related_name='ratings')
    stars = models.IntegerField()  # The star rating given by the user
    comment = models.CharField(max_length=512, blank=True, null=True)  # Optional user comment
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time

    def clean(self):
        """Ensure that the rating is linked to either a song or a playlist, but not both."""
        if not (self.song or self.playlist):
            raise ValidationError("Rating must be linked to either a song or a playlist.")
        if self.song and self.playlist:
            raise ValidationError("Rating cannot be linked to both a song and a playlist at the same time.")

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        rating_info = (
            f"Rating("
            f"user='{self.user.display_name}', "
            f"stars={self.stars}, "
            f"comment='{self.comment[:20] + '...' if self.comment and len(self.comment) > 20 else self.comment or 'None'}', "
            f"created_at={self.created_at.date() if self.created_at else 'N/A'}"
        )

        if self.song:
            rating_info += f", song_id={self.song.spotify_song_id})"
        else:
            rating_info += f", playlist_id={self.playlist.spotify_playlist_id})"

        return rating_info