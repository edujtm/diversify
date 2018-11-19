
import sys
import interfacespfy as isp
import genetic as gen
import pandas as pd
import pprint
import splearn as sp

twousers = False


def get_songs(spfy, userid):
    try:
        return pd.read_csv('csvfiles/' + userid + 'features.csv')
    except FileNotFoundError:
        result = isp.get_user_playlists(spfy, userid, limit=40, features=True)
        return pd.DataFrame(result)


# TODO use argparse to parse CLI
plistname = None

if len(sys.argv) > 1:
    username1 = sys.argv[1]
    username2 = sys.argv[2]
    plistname = ' '.join(sys.argv[3:])
else:
    print("Usage: python3 {0} <username1> <username2> [playlist name]".format(sys.argv[0]))
    sys.exit()

spfy = isp.login_user(username1)

sp.load_mlearn(spfy, users=[username1, username2])
"""
user1 = get_songs(spfy, username1)
user2 = get_songs(spfy, username2)

result = gen.start(spfy, user1, user2=user2)

if plistname is None:
    plistname = 'Diversify Playlist'

pprint.pprint(result)
resultids = result.index.tolist()
isp.tracks_to_playlist(spfy, 'belzedu', trackids=resultids, name=plistname)
"""