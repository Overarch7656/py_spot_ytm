# main.py
import os, json, time, sys, logger
from rich.console import Console
from collections import Counter
from logger import info, success, warn, error

from spotify import (
    spotify_auth,
    get_user_playlists,
    choose_playlists,
    save_playlist_to_json,
    make_safe_filename
)

from ytmusic import (
    load_ytmusic,
    create_playlist,
    add_songs_to_playlist,
    get_playlist_video_ids,
    match_songs_on_ytmusic
)


logger.LOG_TO_FILE = "--log" in sys.argv

console = Console()


def load_saved_playlist(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading playlist file '{path}': {e}[/red]")
        error(f"Error reading playlist file '{path}': {e}")
        return []

def process_playlist(pl, ytmusic):
    playlist_name = pl["name"]
    safe_name = make_safe_filename(playlist_name)
    json_path = f"playlists/{safe_name}.json"

    if not os.path.exists(json_path):
        console.print(f"[red]Missing JSON file for playlist: {playlist_name}[/red]")
        error(f"Missing JSON file for playlist: {playlist_name}")
        return {"name": playlist_name, "status": "missing_json"}

    console.rule(f"[bold yellow]Processing: {playlist_name}[/bold yellow]")
    info(f"Processing playlist: {playlist_name}")
    songs = load_saved_playlist(json_path)
    if not songs:
        return {"name": playlist_name, "status": "empty_json"}

    yt_playlist_id = create_playlist(ytmusic, playlist_name)
    time.sleep(1.5)  # Avoid API timing issues

    video_ids = match_songs_on_ytmusic(ytmusic, songs)
    if not video_ids:
        console.print(f"[orange3]No songs matched for playlist '{playlist_name}'[/orange3]")
        warn(f"No songs matched for playlist '{playlist_name}'")
        return {"name": playlist_name, "status": "no_matches"}

    try:
        add_songs_to_playlist(ytmusic, yt_playlist_id, video_ids)
        time.sleep(1)

        existing_ids = get_playlist_video_ids(ytmusic, yt_playlist_id)
        if Counter(video_ids) == Counter(existing_ids):
            console.print(f"[cyan]Added {len(video_ids)} songs to playlist '{playlist_name}'[/cyan]")
            success(f"Added {len(video_ids)} songs to playlist '{playlist_name}'")
            return {"name": playlist_name, "status": "complete", "added": len(video_ids)}
        else:
            console.print(f"[orange3]Partial success — not all songs were added[/orange3]")
            return {"name": playlist_name, "status": "partial", "added": len(existing_ids)}

    except Exception as e:
        console.print(f"[red]Failed to upload to YouTube Music: {e}[/red]")
        warn(f"Partial upload: not all songs were added to '{playlist_name}'")
        return {"name": playlist_name, "status": "ytmusic_error"}


def main():
    os.makedirs("playlists", exist_ok=True)

    # Spotify Auth & Playlist Export
    sp = spotify_auth()
    playlists = get_user_playlists(sp)
    selected_playlists = choose_playlists(playlists)

    for pl in selected_playlists:
        save_playlist_to_json(sp, pl)

    # YouTube Music Auth
    ytmusic = load_ytmusic()

    # Process Each Playlist
    summary = []
    for pl in selected_playlists:
        try:
            result = process_playlist(pl, ytmusic)
            summary.append(result)
        except Exception as e:
            console.print(f"[red]Unexpected error on '{pl['name']}': {e}[/red]")
            error(f"Unexpected error on '{pl['name']}': {e}")
            summary.append({"name": pl["name"], "status": "crashed"})

    # Final Summary
    console.rule("[bold green]Summary[/bold green]")
    for s in summary:
        status = s["status"]
        if status == "complete":
            console.print(f"[green]✓ {s['name']} — {s['added']} songs added[/green]")
            success(f"{s['name']} — {s['added']} songs added")
        elif status == "partial":
            console.print(f"[orange3]! {s['name']} — partial upload ({s['added']} songs)[/orange3]")
            warn(f"{s['name']} — partial upload ({s['added']} songs)")
        elif status == "no_matches":
            console.print(f"[red]- {s['name']} — no matches found[/red]")
            error(f"{s['name']} — no matches found")
        elif status == "missing_json":
            console.print(f"[red]✘ {s['name']} — playlist file missing[/red]")
            error(f"{s['name']} — playlist file missing")
        elif status == "ytmusic_error":
            console.print(f"[red]✘ {s['name']} — upload error[/red]")
            error(f"{s['name']} — upload error")
        else:
            console.print(f"[red]? {s['name']} — unknown error[/red]")
            error(f"{s['name']} — unknown error")


if __name__ == "__main__":
    main()