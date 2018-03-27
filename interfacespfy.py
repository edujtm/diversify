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
import sys
import csv

_client_id = '5d6d117598a94245a84a726981fa6e3b'
_client_secret = '75df15e303d043a5ad6e65251de5a384'
_redirect_uri = 'http://localhost/'

_scope = ['user-library-read', 'playlist-modify-private']
_fields = ['uri', 'speechiness', 'valence', 'mode', 'liveness', 'key', 'danceability', 'loudness', 'acousticness',
           'instrumentalness', 'energy', 'tempo']

_spfy = None


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


# TODO change description of this function
def get_favorite_songs(spfy, limit=30):
    """

    Queries the spotify WEB API for the logged user's saved musics.
    The token used to log in needs to have the 'user-library-read' permission.
    If that's not the case add it in the interfacespfy.scope array and refresh
    the token.

    :param spfy: spfy object received when logging user
    :param limit: maximum of musics that will be returned from query
    :return: Spotify object (paging object) that reprensents the user's starred music playlist

    """
    results = spfy.current_user_saved_tracks(limit)
    show_tracks(results)
    songs = []
    for item in results['items']:
        song = {field: item['track'][field] for field in ['name', 'id']}
        songs.append(song)
    return songs


def get_user_playlists(spfy, userid, limit=30):
    playlists = []
    playlistpo = spfy.user_playlists(userid, limit)     # Returns a Spotify object (paging object) with playlists
    for playlist in playlistpo['items']:
        if playlist['owner']['id'] == userid:
            result = spfy.user_playlist(userid, playlist['id'], fields="tracks,next")   # return a playlist object
            trackspo = result['tracks']             # Array with information about the tracks in the playlist
            show_tracks(trackspo)
            tracks = []
            for item in trackspo['items']:
                track = {field: item['track'][field] for field in ['name', 'id']}
                tracks.append(track)
            playlists.append(tracks)

    return playlists


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


def wcsv_user_playlists(spfy, userid, limit=30, filename=None):
    """

    Writes a csv file in csvfile/ folder with information about music preferences
    of the user specified with userid (spotify ID). The information is gathered
    from public playlists only. If the user has no public playlists, No information
    can be gathered.

    If the filename is specified it will be written as csvfiles/filename. If it's not
    it'll be written as csvfiles/<userid>features.csv. If the file already exists,
    it's content will be overwritten.

    The limit is the number of songs per playlist that will be gathered. If the playlist
    have less musics than the limit it'll gather the entire playlist.

    :param spfy: spotify.Spotify object received when logging user
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

    _wcsv(featarray, filename)


# TODO change name of this function for a more appropriate one
def wcsv_playlist(spfy, playlist, limit=30, filename="csvfiles/playlistfeatures.csv", quiet=True):

    features = get_features(spfy, playlist, limit=limit, quiet=quiet)
    _wcsv(features, filename)


def get_features(spfy, tracks, limit, quiet=True):
    if limit > 50:
        if quiet:
            print("Limit value cannot be greater than 50")
            return False
        else:
            raise ValueError("Limit value cannot be greater than 50")

    trackids = [track['id'] for track in tracks]
    maxvalue = len(trackids) if len(trackids) < limit else limit + 1  # limit+1 necessary for slicing
    feat = spfy.audio_features(trackids[:maxvalue])
    ffeat = list(_filter_audio_features(feat))
    return ffeat


def _filter_audio_features(analysis):
    for track in analysis:
        ftrack = {field: track[field] for field in _fields}
        yield ftrack


def _wcsv(featarray, filename):
    csvfile = open(filename, 'w')

    csvwriter = csv.DictWriter(csvfile, fieldnames=_fields)
    csvwriter.writeheader()

    for features in featarray:
        csvwriter.writerow(features)

    csvfile.close()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python3 {0} <username>".format(sys.argv[0]))
        sys.exit()
    else:
        username = sys.argv[1]

    print("Logging:", username)
    print("This is a sample program that will search for your saved songs and write them to a file in csvfile/ folder")
    spfy = login_user(username)

    trackids = get_user_playlists(spfy, 'belzedu')

    fsongs = get_favorite_songs(spfy, limit=40)
    wcsv_playlist(spfy, fsongs, limit=40)

    wcsv_user_playlists(spfy, 'biasusan', limit=40)
