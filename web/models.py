from django.db import models

class SpotifyUser(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name
