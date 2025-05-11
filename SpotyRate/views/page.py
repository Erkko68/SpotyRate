from django.shortcuts import render


def landing(request):
    return render(request, "landing.html")

def dashboard(request):
    return render(request, "dashboard.html")

def dashboard_song(request):
    # Render the same dashboard template but with song-specific content
    return render(request, 'dashboard.html', {'active_page': 'song'})

def dashboard_playlist(request):
    # Render the same dashboard template but with song-specific content
    return render(request, 'dashboard.html', {'active_page': 'playlist'})