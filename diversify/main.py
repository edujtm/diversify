import warnings
import pprint
import click
import sys
import os
import pandas as pd
import diversify.genetic as gen
import diversify.utils as utils

from diversify.session import SpotifySession
from diversify.constants import CACHE_FILE

warnings.simplefilter(action='ignore', category=FutureWarning)

twousers = False


def get_songs(spfy, userid):
    try:
        return pd.read_csv('csvfiles/' + userid + 'features.csv')
    except FileNotFoundError:
        result = spfy.get_user_playlists(userid, features=True)
        return pd.DataFrame(result)


@click.group()
def diversify():
    pass


@diversify.command()
def login():
    try:
        utils.login_user()
        click.secho("Logged in successfully", fg='green')
    except utils.DiversifyError as e:
        click.secho(str(e), fg='red')


@diversify.command()
def logout():
    try:
        os.remove(CACHE_FILE)
        click.secho("Logged out successfully", fg='green')
    except OSError:
        click.secho("Already logged out", fg='yellow')


@diversify.command(short_help="creates a playlist using you musical taste")
@click.option('-f', '--friend', help='Your friend Spotify ID')
@click.argument('playlist_name', nargs=-1, required=True)
def playlist(friend, playlist_name):
    """
        
        DIVERSIFY PLAYLIST GENERATOR

        ----------------------------

        This program will create a new playlist in your account based on your
        saved songs and your friend's Spotify public playlists, trying to
        please both of your musical tastes.

        The playlist will be saved on your account.

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
    plistname = ' '.join(playlist_name)

    try:
        spfy = SpotifySession(authenticate=False)
    except utils.DiversifyError as e:
        click.secho(str(e), fg='red')
        sys.exit(1)

    current_user = spfy._current_user
    my_songs = get_songs(spfy, current_user)

    friend_songs = None
    if friend:
        friend_songs = get_songs(spfy, friend)
        click.secho(f"\tGenerating playlist for you and {friend}", fg='green')
    else:
        click.secho("\tGenerating playlist for you", fg='green')

    if friend_songs is not None:
        result = gen.start(spfy, my_songs, user2=friend_songs)
    else:
        result = gen.start(spfy, my_songs)

    pprint.pprint(result)
    trackids = result.index.tolist()
    spfy.tracks_to_playlist(trackids=trackids, name=plistname)


@diversify.command(short_help="downloads csv file with your saved songs")
@click.argument('filename', type=click.Path())
def download(filename):
    """
        This is a small sample code to test if your installation is sucessful.

        It'll access your spotify saved songs and download the songs features
        from the API, saving them in csv format into filename given.
    """
    if filename is None:
        click.echo('Filename was not given')
        sys.exit(0)

    click.echo(f"This is a sample program that will search for your saved songs and write them to {filename}")
    try:
        spfy = SpotifySession(authenticate=False)
    except utils.DiversifyError as e:
        click.secho(str(e), fg='red')
        sys.exit(1)

    fsongs = spfy.get_favorite_songs(features=True)

    dfsongs = pd.DataFrame(fsongs)
    pprint.pprint(dfsongs)
    spfy.playlist_to_csv(fsongs, filename=filename)


if __name__ == '__main__':
    diversify()
