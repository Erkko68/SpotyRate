# SpotyRate

## Introduction
**SpotyRate** is a web application that allows users to discover, rate and comment on songs and playlists using the Spotify API. Unlike Spotify, SpotyRate incorporates its own rating and comment system, as well as a network of friends to encourage musical interaction.

### Features
- Integration with the Spotify public API to retrieve song information.
- Own system of ratings and comments for songs and playlists.
- Management of personal playlists within SpotyRate.
- System of authentication and registration of users.
### Usage (How to deploy)

This project integrates with the Spotify API for user authentication. To make the evaluation process easier for teachers, we have set up a demo Spotify account that bypasses the need to log in with a personal Spotify account, and having to register it to the developer program to obtain the api keys.

Demo login credentials:

    Email: spotyratedemo@gmail.com

    Password: WebProject2025

To run the project locally, execute the following command:

    python3 manage.py runserver
Since the application uses the Spotify API for login, you will need to provide your own API credentials. These can be obtained by registering an application on the Spotify Developer Dashboard.
For testing purposes, you can use the following credentials:

    CLIENT_ID = '198fb21532784721aabf169a007fa26f'
    SECRET_KEY = 'dbb064ba49814f48aadba893a75eec2d'

## CODE

### Models.py
This file contains the definition of the main models of the application database:

User: Represents a user authenticated with Spotify. Their spotify_id, public name (display_name), email (if available) and profile picture are stored.

Song: Represents a song identified by its spotify_song_id.

Playlist: Represents a playlist identified by its spotify_playlist_id.

Rating: Allows a user to rate a song or a playlist (but not both at the same time), with a score (stars) and an optional comment.

Custom validation is included to ensure that each rating is associated with only one song or playlist, never both at the same time.

### Auth.py
This file handles authentication with the Spotify API using OAuth2:

spotify_login(request): Redirects the user to the Spotify login page to obtain the authorization code.

spotify_callback(request): Receives the authorization code, obtains the access token, and retrieves information about the Spotify user. Saves or updates the user in the database.

spotify_logout(request): Logs out of Django and clears session data.

refresh_spotify_token(request): Refreshes the access token using the refresh_token stored in the session to maintain the connection to the API.
### Front-end
The frontend structure is straightforward and easy to understand.
We defined a base file as a template, and the other pages import it to maintain a consistent structure. Initially, this wasn't our approach — we started by hard-coding each page individually. However, we realized that creating a shared template would make the project much easier to maintain and understand in the long run.