
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import sys
import interfacespfy as isp
import genetic as gen
import pandas as pd
import pprint
import argparse

twousers = False


def get_songs(spfy, userid):
    try:
        return pd.read_csv('csvfiles/' + userid + 'features.csv')
    except FileNotFoundError:
        result = isp.get_user_playlists(spfy, userid, limit=40, features=True)
        return pd.DataFrame(result)


description_hint = """
        DIVERSIFY PLAYLIST GENERATOR
        ----------------------------
        
        This program will create a new playlist in your account based on your 
        and your friend's Spotify public playlists, trying to please both of 
        your musical tastes.
        
        The playlist will be saved on the account of the first user.

        The app will redirect you to a page in your browser,
        where you will be asked to login into your spotify account.

        After logging in into your account, you should be redirected to a page
        with the URL pattern as follows:

        http://localhost/?code={code-pattern}

        where you should copy the code-pattern and paste into your terminal. 
        These steps are only necessary once and are a current limitation of the
        spotify WEB API.

        If you prefer, you can also log in through the spotify website into your 
        browser and then run this program, which will not ask for your credentials
        as you'll be already logged in.

        Spotify website: https://www.spotify.com/
    """

parser = argparse.ArgumentParser(description=description_hint, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('user1', help='Your Spotify URI')
parser.add_argument('-u2', '--user2', dest='user2', help="Your friend's Spotify URI")
parser.add_argument('-p', '--playlist_name', nargs='+', default=['Divesify playlist'],
                    dest='playlist_name',
                    help='The name for the playlist that will be created')
args = parser.parse_args()

plistname = ' '.join(args.playlist_name)
username1 = args.user1
username2 = args.user2

spfy = isp.login_user(username1)

user1 = get_songs(spfy, username1)

if username2 is not None:
    user2 = get_songs(spfy, username2)
    result = gen.start(spfy, user1, user2=user2)
else:
    print("empty user2")
    result = gen.start(spfy, user1)

pprint.pprint(result)
resultids = result.index.tolist()
isp.tracks_to_playlist(spfy, username1, trackids=resultids, name=plistname)
