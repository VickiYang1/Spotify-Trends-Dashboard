import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))

# =========================
# 1. FETCH PLAYLIST TRACKS
# =========================

playlist_id = '0sDahzOkMWOmLXfTMf2N4N'
playlist = sp.playlist_items(playlist_id, limit=100)

tracks = []

for item in playlist['items']:
    track = item['track']
    if track:
        primary_artist = track['artists'][0]

        tracks.append({
            'track_id': track['id'],
            'track_name': track['name'],
            'artist_id': primary_artist['id'],
            'artist_name': primary_artist['name'],
            'track_duration_ms': track['duration_ms'],
            'explicit': track['explicit'],
            'popularity': track['popularity'],
            'release_date': track['album']['release_date'],
            'album': track['album']['name'],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
        })

df = pd.DataFrame(tracks)

# convenience columns for visuals
df['track_duration_min'] = df['track_duration_ms'] / 60000

# ================================
# 3. TOP TRACKS FUNCTION (PER ARTIST)
# ================================

def get_artist_top_tracks(artist_id: str, country: str = 'US') -> list[dict]:
    results = sp.artist_top_tracks(artist_id, country=country)
    top_tracks = []

    for track in results['tracks']:
        top_tracks.append({
            'track_id': track['id'],
            'track_name': track['name'],
            'album_name': track['album']['name'],
            'release_date': track['album']['release_date'],
            'duration_ms': track['duration_ms'],
            'duration_min': track['duration_ms'] / 60000,
            'popularity': track['popularity'],
            'explicit': track['explicit'],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
        })

    return top_tracks

# =========================
# 4. BUILD ARTISTS_DF (BATCH)
# =========================

unique_artist_ids = df['artist_id'].dropna().unique().tolist()

artists_data = []

# batch Spotify /artists endpoint for efficiency
for i in range(0, len(unique_artist_ids), 50):
    batch_ids = unique_artist_ids[i:i+50]
    response = sp.artists(batch_ids)

    for artist in response['artists']:
        if not artist:
            continue

        artist_id = artist['id']

        artists_data.append({
            'artist_id': artist_id,
            'artist_name': artist['name'],
            'artist_popularity': artist['popularity'],
            'artist_followers': artist['followers']['total'],
            'artist_genres': ', '.join(artist['genres']) if artist['genres'] else None,
            'artist_image': artist['images'][0]['url'] if artist['images'] else None
        })

artists_df = pd.DataFrame(artists_data)

# ==============================
# 5. BUILD TOP_TRACKS_DF (GLOBAL)
# ==============================

top_tracks_rows = []

for artist_id in unique_artist_ids:
    top_tracks = get_artist_top_tracks(artist_id)
    for t in top_tracks:
        t['artist_id'] = artist_id
        top_tracks_rows.append(t)

top_tracks_df = pd.DataFrame(top_tracks_rows)


# === EXPORT CLEAN DATASETS ===
df.to_csv("spotify_playlist_tracks.csv", index=False)
artists_df.to_csv("spotify_artists.csv", index=False)
top_tracks_df.to_csv("spotify_top_tracks.csv", index=False)
print("successfully exported")