import requests
from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect

from ..models import SpotifyUser

# Load environment variables from .env

SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_REDIRECT_URI = settings.SPOTIFY_REDIRECT_URI

SPOTIFY_LOGOUT_URL = "https://accounts.spotify.com/en/logout"
SPOTIFY_SCOPES = "user-read-private user-read-email"

def spotify_login(request):
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={SPOTIFY_SCOPES}"
    )
    return redirect(auth_url)

def spotify_callback(request):
    """Handle the Spotify OAuth2 callback."""
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    # URL de Spotify para obtener el token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if "access_token" in token_data:
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")

        # Obtener los datos del usuario desde Spotify
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data = requests.get("https://api.spotify.com/v1/me", headers=headers).json()

        # Obtener Spotify ID, nombre y correo del usuario
        spotify_id = user_data["id"]
        display_name = user_data.get("display_name", "Unknown")
        email = user_data.get("email", "")  # Obtener el correo electrónico

        # Obtener la URL de la imagen de perfil (si está disponible)
        images = user_data.get("images", [])
        profile_image_url = images[0].get("url", "") if images else ""

        # Almacenar en la base de datos (si el usuario no existe, se crea)
        user, created = SpotifyUser.objects.get_or_create(
            spotify_id=spotify_id,
            defaults={
                "display_name": display_name,
                "email": email,
                "profile_image_url": profile_image_url,
            }
        )

        # Guardar los tokens en la sesión
        request.session["spotify_access_token"] = access_token
        request.session["spotify_refresh_token"] = refresh_token

        # Redirigir al dashboard
        return redirect("/dashboard/")

    else:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

def spotify_logout(request):
    """
    Logs out the user from Django.
    """
    logout(request)  # Ends the Django authentication session
    request.session.flush()  # Clears all session data
    return redirect('/logout/') # Redirect to log out page

def refresh_spotify_token(request):
    refresh_token = request.session.get("spotify_refresh_token")

    if not refresh_token:
        return JsonResponse({"error": "No refresh token found"}, status=400)

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if "access_token" in token_data:
        request.session["spotify_access_token"] = token_data["access_token"]
        return JsonResponse({"access_token": token_data["access_token"]})
    else:
        return JsonResponse(token_data, status=400)
