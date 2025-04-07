from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("login/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    path("logout/", views.logout, name="logout"),
    path("refresh/", views.refresh_spotify_token, name="spotify_refresh"),

    # Pages
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/song", views.dashboard_song, name="dashboard"),
    path("dashboard/playlist", views.dashboard_playlist, name="dashboard"),

    # Api Data Requests
    path("user/", views.get_spotify_user, name="spotify_user"),

]
