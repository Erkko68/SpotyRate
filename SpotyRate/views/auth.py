import os
import requests
import dotenv
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import logout
from ..models import User

# Load environment variables from .env
dotenv.load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback/"
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
    """Handle the Spotify OAuth2 callback and store user information."""
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    # Request access token
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

    print(token_data)

    if "access_token" not in token_data:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token", "")

    # Retrieve user data from Spotify API
    headers = {"Authorization": f"Bearer {access_token}"}
    user_data = requests.get("https://api.spotify.com/v1/me", headers=headers).json()

    spotify_id = user_data["id"]
    display_name = user_data.get("display_name", "Unknown")
    email = user_data.get("email", "")  # Ensure email is retrieved
    images = user_data.get("images", [])
    profile_image_url = images[0]["url"] if images else ""  # Ensure the image is retrieved

    # Ensure user is updated correctly
    user, created = User.objects.get_or_create(spotify_id=spotify_id)

    # Update fields explicitly
    user.display_name = display_name
    user.email = email
    user.profile_image_url = profile_image_url
    user.save()  # Save the updated user details

    # Save tokens in session
    request.session["spotify_access_token"] = access_token
    request.session["spotify_refresh_token"] = refresh_token

    return redirect("/dashboard/")

def session_logout(request):
    """Logs out the user from Django and clears the session."""
    logout(request)
    request.session.flush()
    return JsonResponse({"OK": "Logged Out"}, status=200)

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
