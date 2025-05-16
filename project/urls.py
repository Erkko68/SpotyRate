"""
URL configuration for project: project.

The `urlpatterns` list routes URLs to views. For more information, please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from SpotyRate import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login and logout
    path("login/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    path("logout/", views.session_logout, name="logout"),
    path("refresh/", views.refresh_spotify_token, name="spotify_refresh"),

    # Pages
    path("", views.landing, name="landing"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/media/', views.media_view, name='media-view'),

    # Api Data Requests
    path("user/", views.get_spotify_user, name="spotify_user"),
    path('api/comment/fetch/', views.media_comments, name='api-media-comments'),
    path('api/comment/submit/', views.submit_comment, name='api-submit-comments'),
    path('api/comment/delete/', views.remove_comment, name='api-remove-comment'),
    path('search/', views.search, name='search'),
]
