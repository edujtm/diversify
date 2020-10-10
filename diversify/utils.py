"""
    This module is made to separate the process of getting the cached token from
    the web browser authentication. If the user already has a cached token, he doesn't
    need to go to the web browser.

    This makes so that is possible to detach a command for login from the other commands.
    the user can call the command: diversify login USERNAME
    and then run all other commands without specifying his username again.
"""
import os
import webbrowser
import configparser
from configparser import ConfigParser
from pathlib import Path

from typing import Optional, NamedTuple, List
from spotipy import oauth2
from diversify.constants import CACHE_FILE, SCOPE, DIVERSIFY_FOLDER


class SpotifyCredentials(NamedTuple):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None


def cached_token(scope: List[str] = None) -> Optional[str]:
    credentials = load_config(DIVERSIFY_FOLDER / 'config.ini')

    str_scope = ' '.join(scope)

    if not credentials.client_id or not credentials.client_secret:
        print_api_help()
        raise DiversifyError('no credentials set')

    sp_oauth = oauth2.SpotifyOAuth(
        *credentials,
        scope=str_scope,
        cache_path=CACHE_FILE
    )

    token_info = sp_oauth.get_cached_token()

    if token_info:
        return token_info['access_token']
    else:
        return None


def auth_token(scope: List[str] = None) -> Optional[str]:
    credentials = load_config(DIVERSIFY_FOLDER / 'config.ini')

    str_scope = ' '.join(scope)

    if not credentials.client_id:
        print_api_help()
        raise DiversifyError('no credentials set')

    sp_oauth = oauth2.SpotifyOAuth(*credentials, scope=str_scope, cache_path=CACHE_FILE)

    print('''

         User authentication requires interaction with your
         web browser. Once you enter your credentials and
         give authorization, you will be redirected to
         a url.  Paste that url you were directed to to
         complete the authorization.

     ''')
    auth_url = sp_oauth.get_authorize_url()
    try:
        webbrowser.open(auth_url)
        print("Opened %s in your browser" % auth_url)
    except:
        print("Please navigate here: %s" % auth_url)

    print()
    print()
    try:
        code = raw_input("Enter the code pattern you were given: ")
    except NameError:
        code = input("Enter the the code pattern you were given: ")
    print()
    print()

    # This call saves the cache file for the token
    token_info = sp_oauth.get_access_token(code)
    if token_info:
        return token_info['access_token']
    else:
        return None


def login_user() -> Optional[str]:
    # Checks if the user is already logged in
    token = cached_token(scope=SCOPE)
    # If it's not, retrieves the token from spotify API
    if not token:
        token = auth_token(scope=SCOPE)

    if not token:
        raise DiversifyError("Unable to login into your account")

    return token


def get_env() -> SpotifyCredentials:
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    return SpotifyCredentials(client_id, client_secret, redirect_uri)


def load_config(path: Path) -> SpotifyCredentials:
    """
        Returns the configuration options of the application.
    """
    try:
        parser = ConfigParser()
        parser.read(path)

        client_secret = parser.get('spotify_api', 'client_secret')
        client_id = parser.get('spotify_api', 'client_id')
        redirect_uri = parser.get('spotify_api', 'redirect_uri')
    except (
        configparser.NoOptionError,
        configparser.NoSectionError,
    ) as e:
        raise DiversifyError(
            f"Could not read configuration files properly:\n {e.message}"
            f"\n\ntry fixing entries in the file {path}"
        )

    return SpotifyCredentials(client_id, client_secret, redirect_uri)


def print_api_help():
    print('''
        You need to set your Spotify API credentials. You can do this by
        setting environment variables like so:

        export SPOTIPY_CLIENT_ID='your-spotify-client-id'
        export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
        export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

        Get your credentials at
            https://developer.spotify.com/my-applications
    ''')


class DiversifyError(Exception):
    """
    Represents any error of usage on Diversify.
    """
    def __init__(self, message):
        super().__init__(message)
