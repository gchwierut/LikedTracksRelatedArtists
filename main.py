import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Spotify API credentials and redirect URI
creds = {
    "client_id": "yourclientid",
    "client_secret": "yoursecretid",
    "redirect_uri": "redirectui",
    "scope": "playlist-modify-public user-library-read"
}

# Initialize Spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(**creds))

# Get the user's liked tracks
results = sp.current_user_saved_tracks(limit=50)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

# Get the distinct artists from the user's liked tracks
artist_ids = set()
for item in tracks:
    for artist in item['track']['artists']:
        artist_ids.add(artist['id'])

# Print the number of distinct artists
print(f"Number of distinct artists: {len(artist_ids)}")

# Get the related distinct artists and their top tracks, and add each track to the new playlist immediately
related_artists = set()
found_top_tracks = set()
playlist_name = "Related Tracks Playlist2"
playlist_id = None
tracks_added = 0

# Load the IDs of the previously retrieved related artists
try:
    with open('related_artists.txt', 'r') as f:
        related_artists.update([line.strip() for line in f])
except FileNotFoundError:
    pass

for artist_id in artist_ids:
    results = sp.artist_related_artists(artist_id)
    for artist in results['artists']:
        if artist['id'] not in artist_ids and artist['id'] not in related_artists:
            related_artists.add(artist['id'])
            # Write the ID of the newly retrieved related artist to the text file
            with open('related_artists.txt', 'a') as f:
                f.write(artist['id'] + '\n')
            if artist['id'] not in found_top_tracks:
                top_tracks = sp.artist_top_tracks(artist['id'], country='PL')
                if len(top_tracks['tracks']) > 0:
                    print(f"Found top track {top_tracks['tracks'][0]['name']} by {artist['name']}")
                    track_id = top_tracks['tracks'][0]['id']
                    if not playlist_id:
                        # Check if the playlist with the given name exists and retrieve its ID
                        playlists = sp.current_user_playlists()
                        for p in playlists['items']:
                            if p['name'] == playlist_name:
                                playlist_id = p['id']
                                break
                        # If the playlist does not exist, create it
                        if not playlist_id:
                            playlist = sp.user_playlist_create(sp.current_user()["id"], playlist_name, public=True)
                            playlist_id = playlist['id']
                    sp.playlist_add_items(playlist_id=playlist_id, items=[track_id])
                    tracks_added += 1
                    found_top_tracks.add(artist['id'])
            if tracks_added >= 11000:  # If 11000 or more tracks have been added, create a new playlist
                playlist_name = f"{playlist_name} {time.time()}"
                playlist_id = None
                tracks_added = 0
