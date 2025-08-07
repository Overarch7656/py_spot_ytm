import json, spotipy, re, os, sys
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from logger import info, success, warn, error

console = Console()


def load_config():
    """
    Loads the Spotify configuration from 'config.json'.

    Returns:
        dict: Configuration dictionary containing Spotify credentials and settings.
    """
    config_path = "config.json"
    if not os.path.exists(config_path):
        console.print("[red]Missing 'config.json'. Please create one using the example_config.json before running this program.[/red]")
        error("Missing 'config.json'. Please create one using the example_config.json before running this program.")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON in 'config.json'. Please fix the format.[/red]")
        error("Invalid JSON in 'config.json'. Please fix the format.")
        sys.exit(1)

def spotify_auth():
    """
    Authenticates the user with Spotify using credentials from 'config.json'.

    Returns:
        spotipy.Spotify: An authenticated Spotify client instance.
    """

    console.print("[bold cyan]Authenticating with Spotify...[/bold cyan]")
    info("Authenticating with Spotify...")

    try:
        config = load_config()["spotify"]

        scope = "playlist-read-private"
        auth_manager = spotipy.SpotifyOAuth(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            scope=scope
        )

        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Confirm auth is valid
        sp.current_user()
        console.print("[green]✔ Successfully authenticated with Spotify[/green]")
        success("Successfully authenticated with Spotify.")
        return sp

    except Exception as e:
        console.print(f"[red]✘ Spotify authentication failed: {e}[/red]")
        error(f"Spotify authentication failed: {e}")
        sys.exit(1)

def get_user_playlists(sp):
    """
    Fetches all user playlists from Spotify.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.

    Returns:
        list[dict]: List of Spotify playlists.
    """

    playlists = []
    offset = 0
    while True:
        response = sp.current_user_playlists(limit=50, offset=offset)
        playlists.extend(response["items"])
        if response["next"]:
            offset += 50
        else:
            break
    return playlists

def make_safe_filename(name):
    """
    Sanitizes a string to be safe for use as a filename.

    Args:
        name (str): Original playlist name.

    Returns:
        str: Sanitized filename.
    """
    return re.sub(r'[^\w\-_\. ]', '_', name).strip()

def is_playlist_saved(name):
    """
    Checks if a playlist with the given name has already been saved as a JSON file.

    Args:
        name (str): Name of the playlist.

    Returns:
        bool: True if the playlist is saved, False otherwise.
    """

    safe_name = make_safe_filename(name)
    path = f"playlists/{safe_name}.json"
    return os.path.exists(path)

def choose_playlists(playlists):
    """
    Prompts the user to select Spotify playlists from a list,
    distinguishing between saved and unsaved ones.

    Args:
        playlists (list[dict]): List of Spotify playlists.

    Returns:
        list[dict]: List of selected playlist dictionaries.
    """

    saved = []
    new = []
    console.rule("[bold cyan]Your Spotify Playlists[/bold cyan]")
    info("Presenting playlist selection...")

    for pl in playlists:
        name = pl["name"]
        label = f"* {name}" if is_playlist_saved(name) else f"  {name}"
        choice = Choice(name=label, value=pl)

        if is_playlist_saved(name):
            saved.append(choice)
        else:
            new.append(choice)

    choices = []
    if new:
        choices.append(Separator("Unsaved Playlists"))
        choices.extend(new)

    if saved:
        choices.append(Separator("Already Saved Playlists (*)"))
        choices.extend(saved)

    selected = inquirer.checkbox(
        message="Select Spotify playlists to convert:",
        choices=choices,
        instruction="(Use arrow keys / space to select)",
        transformer=lambda result: f"Selected {len(result)} playlists"
    ).execute()

    if not selected:
        console.print("[yellow]No playlists selected. Exiting.[/yellow]")
        warn("No playlists selected. Exiting.")
        exit(1)

    return selected

def save_playlist_to_json(sp, playlist):
    """
    Fetches tracks from a Spotify playlist and saves them to a local JSON file.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.
        playlist (dict): Spotify playlist object.

    Returns:
        None
    """
    tracks = []
    results = sp.playlist_items(playlist["id"], additional_types=["track"])
    while results:
        for item in results["items"]:
            track = item["track"]
            if track:
                tracks.append({
                    "title": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"]
                })
        if results["next"]:
            results = sp.next(results)
        else:
            break

    filename = f"playlists/{playlist['name'].replace('/', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=2)

    console.print(f"\n[green]Saved playlist to:[/green] [bold]{filename}[/bold]")
    success(f"Saved playlist to: {filename}")
















