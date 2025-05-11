# SpotyRate

## Overview

SpotyRate is a web application that leverages the Spotify API to let users rate, comment, and share songs and playlists with other users. The main focus is to facilitate interaction and communication among users with similar musical tastes and preferences.

The application adopts a Spotify-inspired theme while incorporating new sections and features to enable users to express their opinions on specific songs and playlists.

### Key Features

* **Rating:** Rate songs using a star-based rating system.
* **Comments:** Share comments and experiences associated with each song and playlist.
* **Friends System:** Unlike Spotify, which relies on Facebook for social connections, SpotyRate implements its own friend system to connect users directly.

Below is the data model structure for the Rating and Comment features:

![Data Model](img.png)

## How to Use

SpotyRate uses Spotify authentication to streamline the login process and prevent multiple login prompts. This integration enables direct interaction with Spotify data.

### Demo Account

To test the application, use the following demo account credentials:

* **Email:** [spotyratedemo@gmail.com](mailto:spotyratedemo@gmail.com)
* **Password:** WebProject2025

If prompted for email verification, select the "Use Password" option or log in to Gmail using the same credentials.

### Admin Access

To access the Admin interface, use these credentials:

* **Username:** admin
* **Password:** admin

### Deployment

To deploy the application, you can use Docker Compose:

```bash
docker-compose build
docker-compose up
```

Alternatively, run the server directly using:

```bash
python3 manage.py runserver
```

### Environment Variables

Ensure that a `.env` file is created in the root directory with the following credentials (linked to the demo account):

```
CLIENT_ID=198fb21532784721aabf169a007fa26f
CLIENT_SECRET=dbb064ba49814f48aadba893a75eec2d
REDIRECT_URI=http://127.0.0.1:8000/callback/
DEBUG=True
```

Ensure that all configurations are properly set before deployment.
