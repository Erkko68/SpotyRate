from django.shortcuts import render
from .auth import spotify_logout

def home(request):
    return render(request, "home.html")

def dashboard(request):
    return render(request, "dashboard.html")

def logout(request):
    # Execute logout function
    spotify_logout(request)
    # Render logout temporary page
    return render(request, "logout.html")

def song(request):
    return render(request, "song.html")