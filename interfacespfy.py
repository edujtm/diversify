"""

    This module makes the connection to the spotify WEB API to get information
    on the user music preferences. It is able to write csv files for playlists
    to be analyzed with future modules.
"""

import spotipy
import spotipy.util as util
import sys

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

    :param token: token received when logging user
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
        print("{0} {1:32.32s} {2:s}".format(idx, track['artists'][0]['name'], track['name']))


def wcsv_from_playlists(spfy, userid, limit=30):
    if limit > 50:
        print("Limit value cannot be greater than 50")
        return False

    playlists = spfy.user_playlists(userid)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == userid:
            results = spfy.user_playlist(userid, playlist['id'], fields="tracks,next")
            tracks = results['tracks']
            #print(tracks)
            #show_tracks(tracks=tracks)
            while tracks['next']:
                tracks = spfy.next(tracks)
                trackids = ['' + item['track']['id'] for item in tracks['items']]
                maxvalue = len(trackids) if len(trackids) < limit else limit+1       # limit+1 necessary for slicing
                print(spfy.audio_features(trackids[:maxvalue]))
    # TODO write csv with custom name for each user. check if file already exists. do not override for simplicity
    return True

def wcsv_audio_analysis(analysis):
    # TODO write caracteristics of a song to a csv file (search useful characterists)
    for item in analysis:
        pass

def wcsv_from_playlist(playlist):
    pass


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python3 {0} <username>".format(sys.argv[0]))
        sys.exit()
    else:
        username = sys.argv[1]

    print(
        "This is a sample program that will search for your saved songs and write them to a csv file in csvfile/ folder")
    spfy = login_user(username)

    result = get_favourite_music(spfy)

    for item in result['items']:
        track = item['track']
        print(track['id'], '-', track['name'], '-', track['artists'][0]['name'])

    # print(spfy.current_user())
    #print(spfy.user_playlist('biasusan'))
    wcsv_from_playlists(spfy, 'biasusan')
