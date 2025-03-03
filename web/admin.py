from django.contrib import admin
from .models import SpotifyUser

@admin.register(SpotifyUser)
class SpotifyUserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "spotify_id", "email", "created_at")  # Columnas visibles en la lista
    search_fields = ("display_name", "spotify_id", "email")  # Campos por los que se puede buscar
    list_filter = ("created_at",)  # Filtros disponibles en el panel lateral

