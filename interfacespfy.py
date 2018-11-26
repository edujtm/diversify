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
import sys, csv, os
import argparse
from dotenv import load_dotenv

load_dotenv()

_client_id = os.getenv("DIVERSIFY_CLIENT_ID")
_client_secret = os.getenv("DIVERSIFY_CLIENT_SECRET")
_redirect_uri = 'http://localhost/'

_scope = ['user-library-read', 'playlist-modify-private']
_fields = ['id', 'speechiness', 'valence', 'mode', 'liveness', 'key', 'danceability', 'loudness', 'acousticness',
           'instrumentalness', 'energy', 'tempo']

_limit = 50


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


def get_favorite_songs(spfy, features=False):
    """
    Queries the spotify WEB API for the logged user's saved musics.
    The token used to log in needs to have the 'user-library-read' permission.
    If that's not the case add it in the interfacespfy.scope array and refresh
    the token.

    Quantity of requests per call = ceil( n° of saved songs / limit )

    :param spfy: spfy object received when logging user
    :param limit: maximum of musics that will be returned from query
    :param features: False -> returns name and id, True -> returns id and features of the song
    :param genres: If it's true, makes another request to the API to get music genre info
    :return: list of dictionaries with name and id keys
    """

    local_limit = 50

    fields = ['name', 'id', 'popularity', 'duration_ms']
    results = spfy.current_user_saved_tracks(local_limit)

    def _get_song_info(json_response):
        result = []
        for item in json_response['items']:
            song = {field: item['track'][field] for field in fields}

            song['album'] = item['track']['album']['name']
            song['album_id'] = item['track']['album']['id']
            song['artist'] = item['track']['artists'][0]['name']
            song['artist_id'] = item['track']['artists'][0]['id']

            result.append(song)
        return result

    songs = _for_all(results, _get_song_info, spfy)

    if features:
        return get_features(spfy, songs)
    else:
        return songs


# TODO add flat feature
def get_user_playlists(spfy, userid, features=False, flat=False):
    """
    Queries the spotify WEB API for the musics in the public playlists
    from the user with the userid (Spotify ID).

    The limit is the number of songs per playlists that will be returned.

    The return is a list of playlists with each being represented by a
    tuple of (name, list of songs (each being a dict with song info)).

    :param spfy: Spotipy session object that is returned when logging user
    :param userid:  The Spotify ID of the playlits' owner
    :param features: If true, gets features instead of song data. default: False
    :return: A list of lists representing songs in each public playlists.
    """

    local_limit = 50

    playlist_query = spfy.user_playlists(userid, local_limit)     # Returns a Spotify object (paging object) with playlists

    # TODO try to change this method to _get_song_info
    def _get_tracks_from_playlist(tracks_paging):
        tracks = []
        for item in tracks_paging['items']:
            track = {field: item['track'][field] for field in ['name', 'id', 'popularity', 'duration_ms']}
            tracks.append(track)
        return tracks

    def _get_all_playlists(playlist_paging):
        result = []
        for playlist in playlist_paging['items']:
            if playlist['owner']['id'] == userid:
                response = spfy.user_playlist(userid, playlist['id'], fields="tracks,next")   # return a playlist object
                trackspo = response['tracks']             # Array with information about the tracks in the playlist
                tracks = _for_all(trackspo, _get_tracks_from_playlist, spfy)
                result.append((playlist['name'], tracks, ))
        return result

    playlists = _for_all(playlist_query, _get_all_playlists, spfy)

    if features:
        result = []
        for playlist in playlists:
            result.extend(get_features(spfy, playlist))
        return result
    else:
        return playlists


def get_new_songs(spfy, seed_tracks, country=None, features=False):

    local_limit = 100
    trackids = [track['id'] for track in seed_tracks]
    fids = np.random.choice(trackids, 5)
    result = spfy.recommendations(seed_tracks=fids.tolist(), limit=local_limit, country=country)
    songs = [{field: track[field] for field in ['id', 'name', 'duration_ms', 'popularity']} for track in result['tracks']]

    if features:
        return get_features(spfy, songs)
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


def user_playlists_to_csv(spfy, userid, filename=None):
    """

    Writes a csv file in csvfile/ folder with information about music preferences
    of the user specified with userid (spotify ID). The information is gathered
    from public playlists only. If the user has no public playlists, No information
    can be gathered.

    If the filename is specified it will be written in the path described by filename.
    If it's not it'll be written as csvfiles/<userid>features.csv. If the file already
    exists, it's content will be overwritten.

    :param spfy: Spotipy session object that is returned when logging user
    :param userid: The user Spotify ID
    :param filename: The name of the csv file to be written in
    :return: None
    """

    if filename is None:
        filename = "csvfiles/" + str(userid) + "features.csv"

    playlists = get_user_playlists(spfy, userid)

    featarray = []
    for playlist in playlists:
        featarray.extend(get_features(spfy, playlist))

    _write_csv(featarray, filename)


def playlist_to_csv(spfy, playlist, filename=None):
    """
    Writes a csv file with the features from a list with songs IDs in the
    path described by filename.

    :param spfy: Spotipy session object that is returned when logging user
    :param playlist: list with songs (dicts with id and name keys)
    :param filename: path where the features will be written
    :return: None
    """
    if not filename:
        filename = 'csvfiles/playlistfeatures.csv'
    features = get_features(spfy, playlist)
    _write_csv(features, filename)


def get_genres(spfy, artists_ids):
    """
            The spofify API currently does not have genres available.
        Left this code here to adapt it for requesting more songs in
        get_favorite_songs() and other methods.

    :param spfy:
    :param artists_ids:
    :return:
    """
    copies = [artist_id for artist_id in artists_ids]
    while copies:
        query, copies = copies[:50], copies[50:]
        response = spfy.albums(query)
        for album in response['albums']:
            if album['genres']:
                yield album['genres'][0]
            else:
                yield 'Not available'


def _for_all(json_response, func, spfy):
    result = []
    while True:
        part = func(json_response)
        result.extend(part)
        if not json_response['next']:
            break
        json_response = spfy.next(json_response)
    return result


def get_features(spfy, tracks):
    """
    Queries the spotify WEB API for the features of a list of songs
    as described by the Audio Analysis object from the Spotify object
    model.

    The returned object is filtered with the fields described in the
    _fields object of the module.

    Quantity of requests per call = ceil( n° of saved songs / 100 )

    :param spfy: Spotipy session object that is returned when logging user
    :param tracks: list with songs (dicts with id and name keys)
    :return: A list with dicts representing audio features
    """

    local_limit = 100
    trackids = [track['id'] for track in tracks]
    all_feat = []

    while trackids:
        query, trackids = trackids[:local_limit], trackids[local_limit:]
        feat = spfy.audio_features(query)
        ffeat = list(_filter_audio_features(feat))
        all_feat.extend(ffeat)

    return all_feat


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


def tracks_to_playlist(spfy, userid, trackids, name=None):
    if name is None:
        name = 'Diversify playlist'
    result = spfy.user_playlist_create(userid, name, public=False)
    spfy.user_playlist_add_tracks(userid, result['id'], trackids)


class HighLimitException(Exception):
    def __init__(self, message):
        super(HighLimitException, self).__init__(message)


if __name__ == '__main__':
    import pprint
    import pandas as pd

    hint = """
        This is a small sample code to test if your installation is sucessful.
        
        It'll access your spotify saved songs and download the songs features 
        from the API, saving them into a csv file in the csvfiles/ folder.
    """

    parser = argparse.ArgumentParser(description=hint, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('user', help='You spotifity URI')
    parser.add_argument('-f', dest='filename', help='The filename where the info is going to be saved')

    args = parser.parse_args()

    username = args.user
    fname = 'playlistfeatures'
    if args.filename:
        fname = args.filename

    print("Logging:", username)
    print("This is a sample program that will search for your saved songs and write them to a file in csvfile/ folder")
    sp = login_user(username)

    fsongs = get_favorite_songs(sp, features=True)

    dfsongs = pd.DataFrame(fsongs)
    pprint.pprint(dfsongs)

    path = 'csvfiles/' + fname + '.csv'
    playlist_to_csv(sp, fsongs, filename=path)
