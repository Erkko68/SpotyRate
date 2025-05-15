from django.contrib.auth.models import BaseUserManager

class SpotifyUserManager(BaseUserManager):
    def create_user(self, spotify_id, **extra_fields):
        if not spotify_id:
            raise ValueError("The Spotify ID must be set")
        user = self.model(spotify_id=spotify_id, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, spotify_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if password is None:
            raise ValueError('Superusers must have a password.')

        user = self.create_user(spotify_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user