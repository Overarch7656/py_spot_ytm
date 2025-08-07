#  Spotify to YouTube Music Playlist Converter (CLI)

This is a terminal-based Python application that lets you:

* Select one or more Spotify playlists
* Export them to a JSON file
* Search and match tracks on YouTube Music
* Create and populate a matching playlist on your YouTube Music account

---

## Features

* Select multiple playlists from your Spotify account
* Detect and highlight already-saved playlist files
* Automatically match tracks on YouTube Music
* Avoid duplicate uploads
* Color-coded terminal UI
* Optional logging and debug modes
* Supports authentication via OAuth for both Spotify and YouTube Music

---

## Requirements

* Python 3.8+
* [Spotify Developer credentials](https://spotipy.readthedocs.io/en/2.25.1/#getting-started)
* [YouTube Data API OAuth credentials](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html)

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/spotyt.git
cd spotyt
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup authentication**

* Create a `config.json` file in the project root. See `example_config.jason`

Example structure:
```json
{
  "spotify": {
    "client_id": "YOUR_SPOTIFY_CLIENT_ID",
    "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
    "redirect_uri": "http://127.0.0.1:9090"
  },
  "yt_secret": {
    "client_id": "YOUR_YOUTUBE_CLIENT_ID",
    "client_secret": "YOUR_YOUTUBE_CLIENT_SECRET"
  }
}
```

4. **Run YouTube Music OAuth flow**

```bash
ytmusicapi oauth
```

This will generate an `oauth.json` file required for authenticating with YouTube Music. You will need your Google API `client_id` and `client_secret. [LINK](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html) *When creating the credentials, select OAuth client ID and pick TVs and Limited Input devices*

---

## Usage

Run the program:

```bash
python main.py
```

Optional flags:

```bash
python main.py --log
```
* `--log`: Saves all output to `logs/session.log`

---

---

## Testing

Tests are written using `unittest`.

Run all tests:

```bash
python -m unittest discover tests
```

---