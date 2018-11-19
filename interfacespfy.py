"""

    This module makes the connection to the spotify WEB API to get information
    on the user music preferences. It is able to write csv files for playlists
    to be analyzed with future modules.

    The goal with this module is to make the spotify data available in a simple
    way for local analysis and interactive analysis with ipython or a jupyter
    notebook.

    This is an experimental project so the preferences are being saved in csv
    files but the music data should be saved in a database or not saved at
    all for privacy reasons.

    --- IMPORTANT ---
    All spotify objects in this module are dicts representing JSON objects defined
    in the Spotify WEB API @link: https://developer.spotify.com/web-api/object-model/
"""

import spotipy
import spotipy.util as util
import numpy as np
import sys
import csv
import os
from dotenv import load_dotenv

load_dotenv()

_client_id = os.getenv("DIVERSIFY_CLIENT_ID")
_client_secret = os.getenv("DIVERSIFY_CLIENT_SECRET")
_redirect_uri = 'http://localhost/'

_scope = ['user-library-read', 'playlist-modify-private']
_fields = ['id', 'speechiness', 'valence', 'mode', 'liveness', 'key', 'danceability', 'loudness', 'acousticness',
           'instrumentalness', 'energy', 'tempo']


def login_user(username, scope=None):
    """
    Logs the user to the Spotify WEB API with permissions declared in scope.
    Default permissions are 'user-library-read' and 'playlist-modify-private'.
    The return object is necessary to make further spotify queries, so this
    should be the first method to be called when using this module.

    :param username: Username to login
    :param scope: Array with permission strings
    :return: spotipy.Spotify object with user session
    """
    if scope is None:
        scope = _scope

    # TODO check if empty scope array will break the api call
    token = util.prompt_for_user_token(username, ' '.join(scope), client_id=_client_id, client_secret=_client_secret,
                                       redirect_uri=_redirect_uri)
    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Not able to get token for:", username)


def get_favorite_songs(spfy, limit=30, features=False):
    """
    Queries the spotify WEB API for the logged user's saved musics.
    The token used to log in needs to have the 'user-library-read' permission.
    If that's not the case add it in the interfacespfy.scope array and refresh
    the token.

    :param spfy: spfy object received when logging user
    :param limit: maximum of musics that will be returned from query
    :return: list of dictionaries with name and id keys
    """
    results = spfy.current_user_saved_tracks(limit)
    show_tracks(results)
    songs = []
    for item in results['items']:
        song = {field: item['track'][field] for field in ['name', 'id']}
        songs.append(song)

    if features:
        return get_features(spfy, songs, limit=limit)
    else:
        return songs


def get_user_playlists(spfy, userid, limit=30, features=False):
    """
    Queries the spotify WEB API for the musics in the public playlists
    from the user with the userid (Spotify ID).

    The limit is the number of songs per playlists that will be returned.

    The return is a list of playlists with each being represented by a
    list of songs (dict with name and id keys).

    :param spfy: Spotipy session object that is returned when logging user
    :param userid:  The Spotify ID of the playlits' owner
    :param limit: Number of songs per playlist
    :return: A list of lists representing songs in each public playlists.
    """
    playlists = []
    playlistpo = spfy.user_playlists(userid, limit)     # Returns a Spotify object (paging object) with playlists
    for playlist in playlistpo['items']:
        if playlist['owner']['id'] == userid:
            result = spfy.user_playlist(userid, playlist['id'], fields="tracks,next")   # return a playlist object
            trackspo = result['tracks']             # Array with information about the tracks in the playlist
            #show_tracks(trackspo)
            tracks = []
            for item in trackspo['items']:
                track = {field: item['track'][field] for field in ['name', 'id']}
                tracks.append(track)
            playlists.append(tracks)

    if features:
        result = []
        for playlist in playlists:
            result.extend(get_features(spfy, playlist, limit=limit))
        return result
    else:
        return playlists


# TODO write tracks to list of dicts
def get_new_songs(spfy, seed_tracks, limit=30, country=None, features=False):
    trackids = [track['id'] for track in seed_tracks]
    fids = np.random.choice(trackids, 5)
    result = spfy.recommendations(seed_tracks=fids.tolist(), limit=limit, country=country)
    songs = [{field: track[field] for field in ['id', 'name'] } for track in result['tracks']]

    if features:
        return get_features(spfy, songs, limit=limit)
    else:
        return songs


def show_tracks(tracks):
    """

    Show tracks from a Spotify object (Paging object) that contains an array of
    dictionaries (JSON objects) representing tracks.

    :param tracks: Spotify paging object
    :return: None
    """
    for idx, item in enumerate(tracks['items']):
        track = item['track']
        print("{0} {1:32.32s} {2:32s}".format(idx, track['artists'][0]['name'], track['name']))


def user_playlists_to_csv(spfy, userid, limit=30, filename=None):
    """

    Writes a csv file in csvfile/ folder with information about music preferences
    of the user specified with userid (spotify ID). The information is gathered
    from public playlists only. If the user has no public playlists, No information
    can be gathered.

    If the filename is specified it will be written in the path described by filename.
    If it's not it'll be written as csvfiles/<userid>features.csv. If the file already
    exists, it's content will be overwritten.

    The limit is the number of songs per playlist that will be gathered. If the playlist
    have less musics than the limit, it'll gather the entire playlist.

    :param spfy: Spotipy session object that is returned when logging user
    :param userid: The user Spotify ID
    :param limit: Maximum number of musics per playlist (maximum of 50)
    :param filename: The name of the csv file to be written in
    :return: None
    """

    if filename is None:
        filename = "csvfiles/" + str(userid) + "features.csv"

    playlists = get_user_playlists(spfy, userid, limit)

    featarray = []
    for playlist in playlists:
        featarray.extend(get_features(spfy, playlist, limit))

    _write_csv(featarray, filename)


def playlist_to_csv(spfy, playlist, limit=30, filename="csvfiles/playlistfeatures.csv"):
    """
    Writes a csv file with the features from a list with songs IDs in the
    path described by filename.

    the limit is the number of songs to be written in the csv file. It is
    currently necessary because the query to the spotify WEB API only has
    a maximum of 50 songs per call.

    If the limit is greater than 50 and quiet is set to True, the function
    will print a warning message and return False without writing anything.
    If it's set to false, it'll raise an Exception.

    :param spfy: Spotipy session object that is returned when logging user
    :param playlist: list with songs (dicts with id and name keys)
    :param limit: The number of songs to be written
    :param filename: path where the features will be written
    :param quiet: When set to false, will raise an exception when limit is too big
    :return: None
    """
    features = get_features(spfy, playlist, limit=limit)
    _write_csv(features, filename)


def get_features(spfy, tracks, limit):
    """
    Queries the spotify WEB API for the features of a list of songs
    as described by the Audio Analysis object from the Spotify object
    model.

    The returned object is filtered with the fields described in the
    _fields object of the module.

    The limit is the number of songs that will be returned. It can be
    set to the number of songs in the tracks list, but it canno't be
    greater than 50.

    If the limit is greater than 50 and quiet is set to True, the function
    will print a warning message and return False without writing anything.
    If it's set to false, it'll raise an Exception.

    :param spfy: Spotipy session object that is returned when logging user
    :param tracks: list with songs (dicts with id and name keys)
    :param limit: The number of songs to be gathered
    :return: A list with dicts representing audio features
    """

    if limit > 50:
        raise ValueError("Limit value cannot be greater than 50")

    trackids = [track['id'] for track in tracks]
    maxvalue = len(trackids) if len(trackids) < limit else limit + 1  # limit+1 necessary for slicing
    feat = spfy.audio_features(trackids[:maxvalue])
    ffeat = list(_filter_audio_features(feat))
    return ffeat


def _filter_audio_features(analysis):
    """
    Internal method to filter the spotify audio features object
    with only the meaningful features.

    :param analysis: List of dicts as returned by the spotify query
    :return: filtered features (Generator)
    """
    for track in analysis:
        ftrack = {field: track[field] for field in _fields}
        yield ftrack


def _write_csv(featarray, filename):
    """
    Write the filtered features in the file described by the
    path in filename.

    :param featarray: List with filtered features
    :param filename: path where the features will be written
    :return: None
    """

    with open(filename, 'w') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=_fields)
        csvwriter.writeheader()

        for features in featarray:
            csvwriter.writerow(features)

        csvfile.close()


def read_csv(filename):

    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)

        featlist = [feature for feature in csvreader]

        return featlist


def tracks_to_playlist(spfy, userid, trackids=None, name=None):
    # TODO finish this function
    if name is None:
        name = 'Diversify playlist'
    result = spfy.user_playlist_create(userid, name, public=False)
    if trackids is not None:
        spfy.user_playlist_add_tracks(userid, result['id'], trackids)


if __name__ == '__main__':
    import pprint

    if len(sys.argv) != 2:
        print("Usage: python3 {0} <username>".format(sys.argv[0]))
        sys.exit()

    username = sys.argv[1]

    print("Logging:", username)
    print("This is a sample program that will search for your saved songs and write them to a file in csvfile/ folder")
    spfy = login_user(username)

    fsongs = get_favorite_songs(spfy, limit=40)
    pprint.pprint(fsongs)
    playlist_to_csv(spfy, fsongs, limit=40)