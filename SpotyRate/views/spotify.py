import requests
from django.http import JsonResponse

def get_spotify_user(request):
    access_token = request.session.get("spotify_access_token")

    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return JsonResponse(response.json())
