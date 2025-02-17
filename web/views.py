import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import logout
from .models import SpotifyUser

# This file contains the api requests from spotify and the internal server.

# Credentials
SPOTIFY_CLIENT_ID = "ab7b2006bff549d7a274837e5ed2a307"
SPOTIFY_CLIENT_SECRET = "4d3687839f2245e3a77500cb1b85344f"
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
    code = request.GET.get("code")  # Ensure 'code' is in the request
    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/callback/",
        "client_id": "ab7b2006bff549d7a274837e5ed2a307",
        "client_secret": "4d3687839f2245e3a77500cb1b85344f",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=data, headers=headers)



    # Ensure the response is not empty
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch token", "details": response.text}, status=response.status_code)
    token_data = response.json()

    request.session["access_token"] = token_data.get("access_token")
    request.session["refresh_token"] = token_data.get("refresh_token")

    try:
        token_info = response.json()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON response from Spotify", "details": response.text}, status=500)

    return redirect("/profile/")

def get_spotify_user(request):
    access_token = request.session.get("spotify_access_token")

    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return JsonResponse(response.json())


def get_spotify_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_url = "https://api.spotify.com/v1/me"

    response = requests.get(user_info_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch user info", "details": response.text}


def spotify_user_profile(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    user_info = get_spotify_user_info(access_token)
    return JsonResponse(user_info)
def refresh_spotify_token(refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    return response.json() if response.status_code == 200 else None


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

def spotify_profile(request):
    access_token = request.session.get("access_token")

    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        return render(request, "profile.html", {"user": user_data})
    else:
        return render(request, "error.html", {"message": "Failed to fetch profile"})
