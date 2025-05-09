from django.db import models
from django.core.exceptions import ValidationError

class User(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)  # Unique Spotify user ID
    display_name = models.CharField(max_length=255)  # Spotify display name
    email = models.EmailField(blank=True, null=True)  # Optional email address
    profile_image_url = models.URLField(blank=True, null=True)  # Optional profile image URL
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time

    def __str__(self):
        return self.display_name

class Song(models.Model):
    spotify_song_id = models.CharField(max_length=100, unique=True)  # Unique Spotify song ID

    def __str__(self):
        return self.spotify_song_id

class Playlist(models.Model):
    spotify_playlist_id = models.CharField(max_length=100, unique=True)  # Unique Spotify playlist ID

    def __str__(self):
        return self.spotify_playlist_id

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    # Either a song or a playlist must be linked, but not both at the same time.
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
        if self.song:
            linked_item = f"Song: {self.song.spotify_song_id}"
        else:
            linked_item = f"Playlist: {self.playlist.spotify_playlist_id}"
        return f"{self.user.display_name} rated {linked_item} - {self.stars} stars"
