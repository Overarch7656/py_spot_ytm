import os, sys, json
from ytmusicapi import YTMusic, OAuthCredentials
from rich.console import Console
from logger import info, success, error

console = Console()

OAUTH_PATH = "oauth.json"
CLIENT_SECRET_PATH = "config.json"  # You (the user/god emperor/ cool guy) create this with your client_id and client_secret


def load_ytmusic():
    """
    Loads YouTube Music authentication using oauth.json and a client credentials file.
    Returns:
        YTMusic: An authenticated YTMusic instance.
    """
    if not os.path.exists(OAUTH_PATH):
        console.print("[red]Missing 'oauth.json'. Run 'ytmusicapi oauth' in your terminal to generate it.[/red]")
        console.print("[yellow]You will need a client_id and secret from Google's API README[/yellow]")
        error("Missing 'oauth.json'. Run 'ytmusicapi oauth' in your terminal to generate it.")
        sys.exit(1)

    if not os.path.exists(CLIENT_SECRET_PATH):
        console.print(f"[red]Missing '{CLIENT_SECRET_PATH}'. Create this file with your YouTube client_id and client_secret.[/red]")
        error(f"Missing '{CLIENT_SECRET_PATH}'. Create this file with your YouTube client_id and client_secret.")
        sys.exit(1)

    try:
        with open(CLIENT_SECRET_PATH, "r", encoding="utf-8") as f:
            creds = json.load(f)
            yt_creds = creds["yt_secret"]
            client_id = yt_creds["client_id"]
            client_secret = yt_creds["client_secret"]

        oauth_credentials = OAuthCredentials(
            client_id=client_id,
            client_secret=client_secret
        )

        console.print("[bold cyan]Authenticating with YouTube Music...[/bold cyan]")
        info("Authenticating with YouTube Music...")
        yt = YTMusic(OAUTH_PATH, oauth_credentials=oauth_credentials)
        console.print("[green]✔ Successfully authenticated with YouTube Music[/green]")
        return yt

    except Exception as e:
        console.print("[red]✘ YouTube Music authentication failed[/red]")
        console.print(f"[red]{e}[/red]")
        error(f"YouTube Music authentication failed: {e}")
        sys.exit(1)

def create_playlist(ytmusic, name, description="Imported from Spotify"):
    """
    Creates a new playlist on YouTube Music.

    Args:
        ytmusic (YTMusic): Authenticated YTMusic instance.
        name (str): Name of the playlist.
        description (str, optional): Playlist description. Defaults to "Imported from Spotify".

    Returns:
        str: The ID of the newly created playlist.
    """

    try:
        console.print(f"[cyan]Creating playlist: '{name}'[/cyan]")
        info(f"Creating playlist: '{name}'")
        return ytmusic.create_playlist(name, description=description)
    except Exception as e:
        console.print(f"[red]Failed to create playlist '{name}': {e}[/red]")
        error(f"Failed to create playlist '{name}': {e}")
        sys.exit(1)

def search_song(ytmusic, title, artist):
    """
    Searches YouTube Music for a song by title and artist.

    Args:
        ytmusic (YTMusic): Authenticated YTMusic instance.
        title (str): Song title.
        artist (str): Song artist.

    Returns:
        str | None: Video ID of the found song, or None if not found.
    """

    console.print(f"[cyan] Searching for {title} - {artist}[/cyan]")
    info(f"Searching for {title} - {artist}")
    try:
        query = f"{title} {artist}"
        results = ytmusic.search(query, filter="songs")
        if results:
            return results[0].get("videoId")
    except Exception as e:
        console.print(f"[orange3]Search failed for '{title} - {artist}': {e}[/orange3]")
        error(f"Search failed for '{title} - {artist}': {e}")
    return None

def add_songs_to_playlist(ytmusic, playlist_id, video_ids):
    """
    Adds a list of video IDs to a YouTube Music playlist.

    Args:
        ytmusic (YTMusic): Authenticated YTMusic instance.
        playlist_id (str): YouTube Music playlist ID.
        video_ids (list[str]): List of YouTube Music video IDs.

    Returns:
        None
    """

    try:
        console.print(f"[cyan]Adding {len(video_ids)} songs to playlist[/cyan]")
        info(f"Adding {len(video_ids)} songs to playlist...")
        ytmusic.add_playlist_items(playlist_id, video_ids, duplicates=True)
    except Exception as e:
        console.print(f"[red]Failed to add songs to playlist: {e}[/red]")
        error(f"Failed to add songs to playlist: {e}")
        sys.exit(1)

def get_playlist_video_ids(ytmusic, playlist_id):
    """
    Fetches a YouTube Music playlist by ID and returns a list of video IDs.

    Args:
        ytmusic (YTMusic): Authenticated YTMusic instance.
        playlist_id (str): YouTube Music playlist ID.

    Returns:
        list[str]: List of video IDs in the playlist.
    """
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=5000)
        return [
            track["videoId"]
            for track in playlist.get("tracks", [])
            if "videoId" in track
        ]
    except Exception as e:
        console.print(f"[red]Failed to fetch playlist '{playlist_id}': {e}[/red]")
        error(f"Failed to fetch playlist '{playlist_id}': {e}")
        return []

def match_songs_on_ytmusic(ytmusic, songs):
    """
    Matches a list of songs with their corresponding YouTube Music video IDs.

    Args:
        ytmusic (YTMusic): Authenticated YTMusic instance.
        songs (list[dict]): List of songs with 'title' and 'artist' fields.

    Returns:
        list[str]: List of matched video IDs (duplicates removed).
    """

    video_ids = []
    for song in songs:
        title, artist = song['title'], song['artist']
        video_id = search_song(ytmusic, title, artist)
        if video_id:
            console.print(f"[green]✔ {title} - {artist}[/green]")
            success(f"{title} - {artist}")
            video_ids.append(video_id)
        else:
            console.print(f"[red]✘ NOT FOUND: {title} - {artist}[/red]")
            error(f"NOT FOUND: {title} - {artist}")
    return list(dict.fromkeys(video_ids))  # Remove any duplicates

