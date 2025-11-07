from spotify_client import get_spotify_client
sp = get_spotify_client()

# Example: get an artist
artist = sp.search(q="The Weeknd", type="artist")
print(artist['artists']['items'][0]['name'])

print(sp.playlist("37i9dQZEVXbMDoHDwVN2tF")["name"])
