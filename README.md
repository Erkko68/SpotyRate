# SpotyRate

## Introduction
**SpotyRate** is a web application that allows users to discover, rate and comment on songs and playlists using the Spotify API. Unlike Spotify, SpotyRate incorporates its own rating and comment system, as well as a network of friends to encourage musical interaction.

### Features
- Integration with the Spotify public API to retrieve song information.
- Own system of ratings and comments for songs and playlists.
- Management of personal playlists within SpotyRate.
- System of authentication and registration of users.
### Usage (How to deploy)

email: spotyratedemo@gmail.com

contrasenya: WebProject2025

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