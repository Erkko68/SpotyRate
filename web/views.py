import requests
import os
import dotenv
from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import logout
from .models import SpotifyUser

# This file contains the api requests from spotify and the internal server.

# Load environment variables from .env
dotenv.load_dotenv()

# Access the variables
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback/"
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

'''
Callback is a api request that grabs the authentication code from Spotify
Its specified in the Spotify Api as the callback request after the user
performs the login.
'''
def spotify_callback(request):
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    # Exchange code for token
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

        # Fetch user info from Spotify
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
        spotify_id = user_data["id"]
        display_name = user_data.get("display_name", "Unknown")

        # Store in DB (if new user, create one)
        user, _ = SpotifyUser.objects.get_or_create(
            spotify_id=spotify_id,
            defaults={"display_name": display_name}
        )

        # Save tokens in session
        request.session["spotify_access_token"] = access_token
        request.session["spotify_refresh_token"] = refresh_token

        return redirect("/dashboard/")  # Redirect to dashboard
    else:
        return redirect("/login/")

def get_spotify_user(request):
    access_token = request.session.get("spotify_access_token")

    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return JsonResponse(response.json())

'''
Refreshes the authorization code from the user, since Spotify authorization code
only lasts for one hour we have to automatically request a a refresh in case an user
is more than that time in the app.
'''
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


# Render Requests for the main pages
def dashboard(request):
    return render(request, "dashboard.html")
def home(request):
    return render(request,"home.html")

def logout_view(request):
    logout(request)  # Ends Django session
    request.session.flush()  # Clears all session data
    return redirect("/")  # Redirect to home after logging out
