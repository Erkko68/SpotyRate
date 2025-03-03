 from django.db import models

class SpotifyUser(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)  # ID único de Spotify
    display_name = models.CharField(max_length=255)  # Nombre de usuario de Spotify
    email = models.EmailField(blank=True, null=True)  # Correo electrónico del usuario
    profile_image_url = models.URLField(blank=True, null=True)  # URL de la imagen de perfil (si es necesario)
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return self.display_name
