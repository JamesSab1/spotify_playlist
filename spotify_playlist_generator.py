import sys
import configparser
import spotipy
from spotipy import util


def user_input():
    try:
        artist = raw_input("Artist name:\n")
        track = raw_input("Song title:\n")

        results = sp.search(q='artist:' + artist + ' track:' + track, type='track')
        track_id = results['tracks']['items'][0]['id']
        artist_id = results['tracks']['items'][0]['artists'][0]['id']
        track_info = sp.track(track_id)
        track_name = track_info['name']

        return (results, track_id, artist_id, track_name)
    except:
        print("Invalid input...")
        return 9999


def add_track():
    results = user_input()
    if results != 9999:
        track_ids.append(results[1])
        return "Track added: " + str(results[3]) + '\n'


def add_artists_top_ten_tracks():
    try:
        name = raw_input("Search artist:\n")
        results = sp.search(q='artist:' + name, type='artist')
        spotify_id = results['artists']['items'][0]['id']
        spotify_id = 'spotify:artist:' + spotify_id
        top_ten = sp.artist_top_tracks(spotify_id)
        for i in range(0, 9):
            track_ids.append(top_ten['tracks'][i]['id'])
        return "Added artist's top ten tracks\n"
    except:
        return "invalid input..."


def add_album_tracks():
    results = user_input()
    if results != 9999:
        album_id = results[0]['tracks']['items'][0]['album']['id']
        album_tracks = sp.album_tracks(album_id)
        # iterate over the number of tracks on the album
        for i in range(0, len(album_tracks['items'])):
            track_ids.append(album_tracks['items'][i]['id'])
        return "Added album tracks\n"


def add_track_recommend():
    results = user_input()
    if results != 9999:
        n = int(raw_input("How many? Max 50\n"))
        if isinstance(n, (int, long)):
            recommend = sp.recommendations(seed_tracks=[results[1]], limit=n)
            for i in range(0, n):
                track_ids.append(recommend['tracks'][i]['id'])
            return "Recommended tracks added\n"
        else:
            return "Invalid input: " + str(n)


def add_related_artists_top_tracks():
    try:
        name = raw_input("Search related artists to:\n")
        results = sp.search(q='artist:' + name, type='artist')
        spotify_id = results['artists']['items'][0]['id']
        spotify_id = 'spotify:artist:' + spotify_id

        related_artists = sp.artist_related_artists(spotify_id)
        for artist in related_artists['artists']:
            results = sp.artist_top_tracks(artist['id'])
            for i in range(0, 3):
                track_ids.append(results['tracks'][i]['id'])
        return "Related artists top tracks added"
    except:
        return "Invalid input..."


def view_playlist():
    try:
        playlist_id = add_to_playlist()
        results = sp.user_playlist_tracks(username, playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        for track in tracks:
            print(track['track']['name'])
        # remove songs as we only want to add them once when exiting
        sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id,
                                                          track_ids)
        return "playlist complete"
    except:
        return "Empty playlist..."


def add_to_playlist():
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:  # iterate through playlists
        if playlist['name'] == playlist_name:  # filter for playlist
            playlist_id = playlist['id']
    sp.user_playlist_add_tracks(username, playlist_id, track_ids)
    return playlist_id


def delete_playlist():
    global track_ids
    track_ids = []
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:  # iterate through playlists
        if playlist['name'] == playlist_name:  # filter for playlist
            playlist_id = playlist['id']
            sp.user_playlist_unfollow(username, playlist_id)
            return "Playlist deleted\n"
        else:
            return "Playlist already deleted\n"


def exit_menu():
    try:
        add_to_playlist()
    except:
        print("Empty playlist...")
    print('Exiting...')
    sys.exit()


def menu(argument):
    switcher = {
        '1': add_track,
        '2': add_artists_top_ten_tracks,
        '3': add_album_tracks,
        '4': add_track_recommend,
        '5': add_related_artists_top_tracks,
        '6': view_playlist,
        '7': delete_playlist,
        '8': exit_menu
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: 'Invalid entry...\n')
    # Execute the function
    print func()


# set up spotipy object with credentials

# hide credentials
config = configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')
username = config.get('SPOTIFY', 'USERNAME')

token = util.prompt_for_user_token(username, scope="playlist-modify-public",
                                   client_id=client_id, client_secret=client_secret,
                                   redirect_uri='http://localhost:8888/callback')
# scope needs to be added to edit user playlists -
# https://stackoverflow.com/questions/56173066/how-to-solve-insufficient-client-scope-in-python-using-spotipy
# need to whitelist redirect_uri in developer app - dashboard -> app -> edit settings
sp = spotipy.Spotify(auth=token)


playlist_name = str(raw_input('Enter Playlist Name\n'))
sp.user_playlist_create(username, name=playlist_name)
track_ids = []

# main loop

ans = ''
while ans not in ['q', 'Q']:
    print("""             1: add_track,
             2: add_artists_top_ten_tracks,
             3: add_album_tracks,
             4: add_track_recommend,
             5: add_related_artists_top_tracks,
             6: view_playlist,
             7: delete_playlist
             8: exit_menu""")
    ans = raw_input('Select choice [1-7]:\n')
    menu(ans)

if ans in ['q', 'Q']:
    ans = raw_input("Do you want to add songs to playlist? Y/N\n")
    if ans in ['y', 'Y']:
        try:
            add_to_playlist()
        except:
            print("no songs added to playlist\n")
