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

    All spotify objects in this module are dicts representing JSON objects
    defined in the Spotify WEB API @link:
    https://developer.spotify.com/web-api/object-model/
"""
import argparse
import csv
import os
import json
import asyncio
import spotipy
import spotipy.util as util
import numpy as np

import diversify.utils as utils
from diversify.asyncutils import gather_pages
from diversify.types import SongMetadata, AudioFeatures, SongWithFeatures, \
        JsonObject, Playlist

from typing import List, Callable, Any, Tuple, \
    Dict, Union, Optional, Iterator

from diversify.constants import SCOPE


_fields = ['id', 'speechiness', 'valence', 'mode', 'liveness', 'key',
           'danceability', 'loudness', 'acousticness', 'instrumentalness',
           'energy', 'tempo']

_limit = 50


def _get_session(authenticate: bool = True) -> spotipy.Spotify:
    if authenticate:
        token = utils.login_user()
    else:
        token = utils.cached_token(scope=SCOPE)

    if token:
        return spotipy.Spotify(auth=token)
    else:
        if authenticate:
            raise utils.DiversifyError(f"Unable to log in to your account")
        else:
            raise utils.DiversifyError(
                "You are not logged in. Run [diversify login] to log in."
            )


class SpotifySession:
    def __init__(self, authenticate: bool = True):
        """
        Logs the user to the Spotify WEB API with permissions declared in
        scope. Default permissions are 'user-library-read' and
        'playlist-modify-private'.

        If the authenticate is false, it'll get information from cache. In
        other words, it assumes it's already logged.

        :param authenticate: If true, use web browser authentication,
            else cached info.
        """

        self._session = _get_session(authenticate)
        self._current_user = self._session.current_user()['id']

    def _for_all(
            self,
            json_response: JsonObject,
            func: Callable[[JsonObject], List[Any]]
    ) -> List[Any]:
        """
        Requests all pages from a paginated response.

        :param json_response: A pagination object returned from a http request
        :param func: Function that parses a pagination object into a list of objects
        :return: All the data gathered from all the pages
        """
        jsons = asyncio.run(gather_pages(self._session, json_response))

        result = []
        for json in jsons:
            result.extend(func(json))

        return result

    @staticmethod
    def _write_csv(featarray: List[AudioFeatures], filename: str) -> None:
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

    @staticmethod
    def _get_song_info(json_response: JsonObject) -> List[SongMetadata]:
        fields = ['name', 'id', 'popularity', 'duration_ms']

        result = []
        for item in json_response['items']:
            song = {field: item['track'][field] for field in fields}

            song['album'] = item['track']['album']['name']
            song['album_id'] = item['track']['album']['id']
            song['artist'] = item['track']['artists'][0]['name']
            song['artist_id'] = item['track']['artists'][0]['id']

            result.append(song)
        return result

    @staticmethod
    def _filter_audio_features(analysis) -> Iterator[AudioFeatures]:
        """
        Internal method to filter the spotify audio features object
        with only the meaningful features.

        :param analysis: List of dicts as returned by the spotify query
        :return: filtered features (Generator)
        """
        for track in analysis:
            ftrack = {field: track[field] for field in _fields}
            yield ftrack

    def get_features(
            self,
            tracks: List[SongMetadata],
            limit: int = 10
    ) -> List[AudioFeatures]:
        """
        Queries the spotify WEB API for the features of a list of songs
        as described by the Audio Analysis object from the Spotify object
        model.

        The returned object is filtered with the fields described in the
        _fields object of the module.

        Quantity of requests per call = ceil( n° of saved songs / 100 )

        :param limit:
        :param tracks: list with songs (dicts with id and name keys)
        :return: A list with dicts representing audio features
        """

        local_limit = limit
        trackids = [track['id'] for track in tracks]
        all_feat = []

        while trackids:
            query, trackids = trackids[:local_limit], trackids[local_limit:]
            feat = self._session.audio_features(query)
            ffeat = list(self._filter_audio_features(feat))
            all_feat.extend(ffeat)

        return all_feat

    def get_favorite_songs(
        self,
        features: bool = False
    ) -> Union[List[SongMetadata], SongWithFeatures]:
        local_limit = 50

        results = self._session.current_user_saved_tracks(local_limit)

        songs = self._for_all(results, self._get_song_info)

        if features:
            song_features = self.get_features(songs)
            return SongWithFeatures(songs, song_features)
        else:
            return songs

    def get_user_playlists(
            self,
            userid: Optional[str] = None,
            limit: int = 10,
            features: bool = False,
            flat: bool = False
    ):
        """
            Queries the spotify WEB API for the musics in the public playlists
            from the user with the userid (Spotify ID).

            if userid is not passed, it will get the playlists songs from the
            current logged user.

            The limit is the number of songs per playlists that will be returned.

            The return is a list of playlists with each being represented by a
            tuple of (name, list of songs (each being a dict with song info)).

            If flat is True, all playlists are going to be merged into one big list.

            :param userid:  The Spotify ID of the playlits' owner
            :param limit: limit for the pagination API
            :param features: If true, gets features instead of song data. default: False
            :param flat: flattens the result
            :return: A list of tuples representing playlists for each public playlist of userid.
            """

        local_limit = limit

        if not userid:
            userid = self._current_user

        # Returns a Spotify object (paging object) with playlists
        playlist_query = self._session.user_playlists(userid, local_limit)

        def _get_all_playlists(playlist_paging):
            result = []
            for playlist in playlist_paging['items']:
                if playlist['owner']['id'] == userid:
                    # return a playlist object
                    response = self._session.user_playlist(
                        userid, playlist['id'], fields="tracks,next")
                    trackspo = response[
                        'tracks']  # Array with information about the tracks in the playlist
                    tracks = self._for_all(trackspo, self._get_song_info)
                    result.append((playlist['name'], tracks,))
            return result

        playlists = self._for_all(playlist_query, _get_all_playlists)

        result = playlists
        if features:
            result = [(name, self.get_features(playlist)) for name, playlist in playlists]

        if not flat:
            return result

        flattened = []
        for name, playlist in result:
            flattened.extend(playlist)
        return flattened

    def get_new_songs(self,
                      seed_tracks: List[SongMetadata],
                      country: Optional[str] = None,
                      features: bool = False):
        local_limit = 100
        trackids = [track['id'] for track in seed_tracks]
        fids = np.random.choice(trackids, 5)
        result = self._session.recommendations(
            seed_tracks=fids.tolist(), limit=local_limit, country=country)
        songs = [{field: track[field] for field in ['id', 'name', 'duration_ms', 'popularity']} for
                 track in result['tracks']]

        if features:
            return self.get_features(songs)
        else:
            return songs

    def show_tracks(self, tracks: JsonObject) -> None:
        """

        Show tracks from a Spotify object (Paging object) that contains an array of
        dictionaries (JSON objects) representing tracks.

        :param tracks: Spotify paging object
        :return: None
        """
        for idx, item in enumerate(tracks['items']):
            track = item['track']
            print("{0} {1:32.32s} {2:32s}".format(idx, track['artists'][0]['name'], track['name']))

    def user_playlists_to_csv(self, userid: Optional[str], filename: Optional[str] = None) -> None:
        """

        Writes a csv file in csvfile/ folder with information about music preferences
        of the user specified with userid (spotify ID). The information is gathered
        from public playlists only. If the user has no public playlists, No information
        can be gathered.

        If the filename is specified it will be written in the path described by filename.
        If it's not it'll be written as csvfiles/<userid>features.csv. If the file already
        exists, it's content will be overwritten.

        :param userid: The user Spotify ID
        :param filename: The name of the csv file to be written in
        :return: None
        """

        if not userid:
            userid = self._current_user

        if filename is None:
            filename = "csvfiles/" + str(userid) + "features.csv"

        all_songs = self.get_user_playlists(userid, flat=True)
        featarray = self.get_features(all_songs)

        self._write_csv(featarray, filename)

    def playlist_to_csv(
            self,
            playlist: List[SongMetadata],
            filename: Optional[str] = None
    ) -> None:
        """
        Writes a csv file with the features from a list with songs IDs in the
        path described by filename.

        :param playlist: list with songs (dicts with id and name keys)
        :param filename: path where the features will be written
        :return: None
        """
        features = self.get_features(playlist)
        self._write_csv(features, filename or 'csvfiles/playlistfeatures.csv')

    def get_genres(self, artists_ids) -> Iterator[str]:
        """
        The spofify API currently does not have genres available.
        Left this code here to adapt it for requesting more songs in
        get_favorite_songs() and other methods.
        :param artists_ids:
        :return:
        """
        copies = [artist_id for artist_id in artists_ids]
        while copies:
            query, copies = copies[:50], copies[50:]
            response = self._session.albums(query)
            for album in response['albums']:
                if album['genres']:
                    yield album['genres'][0]
                else:
                    yield 'Not available'

    def tracks_to_playlist(self, trackids: List[SongMetadata], name: Optional[str] = None) -> None:
        if name is None:
            name = 'Diversify playlist'
        userid = self._current_user
        result = self._session.user_playlist_create(userid, name, public=False)
        self._session.user_playlist_add_tracks(userid, result['id'], trackids)


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

    parser = argparse.ArgumentParser(description=hint,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-f', dest='filename',
                        help='The filename where the info is going to be saved')

    args = parser.parse_args()

    fname = 'playlistfeatures'
    if args.filename:
        fname = args.filename

    print(
        "This is a sample program that will search for your saved songs and write them to a file in csvfile/ folder")

    sp = SpotifySession()

    fsongs = sp.get_favorite_songs(features=True)

    dfsongs = pd.DataFrame(fsongs.songs)
    pprint.pprint(dfsongs)

    path = 'csvfiles/' + fname + '.csv'
    sp.playlist_to_csv(fsongs.features, filename=path)
