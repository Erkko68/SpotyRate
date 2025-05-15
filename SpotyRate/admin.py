from django.contrib import admin
from .models import SpotifyUser, Media, Rating

admin.site.register(SpotifyUser)
admin.site.register(Media)
admin.site.register(Rating)

class SpotifyUserAdmin(admin.ModelAdmin):
    list_display = ('spotify_id', 'display_name', 'email', 'is_staff', 'is_active')
    search_fields = ('spotify_id', 'display_name', 'email')
