from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    path("user/", views.get_spotify_user, name="spotify_user"),
    path("refresh/", views.refresh_spotify_token, name="spotify_refresh"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('logout/', views.logout_view, name='logout'),
]
