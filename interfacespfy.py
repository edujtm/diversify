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
"""

import spotipy
import spotipy.util as util
import sys
import csv

_client_id = '5d6d117598a94245a84a726981fa6e3b'
_client_secret = '75df15e303d043a5ad6e65251de5a384'
_redirect_uri = 'http://localhost/'
_scope = ['user-library-read', 'playlist-modify-private']


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


def get_favourite_music(spfy, limit=20):
    """

    Queries the spotify WEB API for the logged user's saved musics.
    The token used to log in needs to have the 'user-library-read' permission.
    If that's not the case add it in the interfacespfy.scope array and refresh
    the token.

    :param spfy: spfy object received when logging user
    :param limit: maximum of musics that will be returned from query
    :return: spotipy object that reprensents the user's starred music

    """
    results = spfy.current_user_saved_tracks(limit)
    return results


def get_public_playlists(spfy, userid, limit=50, offset=0):
    playlists = spfy.user_playlists(userid, limit, offset)
    return playlists


def show_tracks(tracks):
    for idx, item in enumerate(tracks['items']):
        track = item['track']
        print("{0} {1:32.32s} {2:s} - {3}".format(idx, track['artists'][0]['name'], track['name'], track['id']))


def wcsv_from_playlists(spfy, userid, limit=30, filename=None):
    if limit > 50:
        print("Limit value cannot be greater than 50")
        return False

    if filename is None:
        filename = str(userid) + "features.csv"

    try:
        csvfile = open('csvfiles/' + filename, 'w')             # Needs to be here so the call to open occurs only once
    except FileExistsError:
        print("File already exists locally in csvfiles/{0}. Remove it and rerun to update.".format(filename))
        return False

    # Start the writer and writes the header for the track analysis
    fields = ['uri', 'speechiness', 'valence', 'mode', 'liveness', 'key', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'energy', 'tempo']
    csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
    csvwriter.writeheader()

    playlists = spfy.user_playlists(userid)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == userid:
            results = spfy.user_playlist(userid, playlist['id'], fields="tracks,next")     # return a playlist object
            tracks = results['tracks']
            # print(tracks)
            show_tracks(tracks=tracks)
            features = _get_features_with_limit(spfy, tracks, limit)
            _wcsv_audio_analysis(features, csvwriter, fields)

    csvfile.close()
    return True


def _get_features_with_limit(spfy, tracks, limit):
    trackids = [item['track']['id'] for item in tracks['items']]
    maxvalue = len(trackids) if len(trackids) < limit else limit+1       # limit+1 necessary for slicing
    return spfy.audio_features(trackids[:maxvalue])


def _wcsv_audio_analysis(analysis, csvwriter, fields):
    # TODO write caracteristics of a song to a csv file (search useful characterists)
    for track in analysis:
        ftrack = {field : track[field] for field in fields}
        csvwriter.writerow(ftrack)


def wcsv_from_playlist(playlist):
    pass


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python3 {0} <username>".format(sys.argv[0]))
        sys.exit()
    else:
        username = sys.argv[1]

    print("Logging:", username)
    print(
        "This is a sample program that will search for your saved songs and write them to a csv file in csvfile/ folder")
    spfy = login_user(username)

    result = get_favourite_music(spfy)

    for item in result['items']:
        track = item['track']
        print(track['id'], '-', track['name'], '-', track['artists'][0]['name'])

    # print(spfy.current_user())
    #print(spfy.user_playlist('maxmyllercarvalho'))
    wcsv_from_playlists(spfy, 'maxmyllercarvalho')
