from unittest.mock import Mock, patch, call
import pytest
from faker import Faker
import spotipy as spt
from diversify.session import SpotifySession, _get_session, _fields

fake = Faker()
Faker.seed(0)

# I'm using this project as a way to learn how to test functions
# and isolate dependencies, so there might be a bunch of useless tests here
# and overly mocked tests that tests implementation

# ------  Fixtures  -------


@pytest.fixture()
def spotify_session(mocker):
    """
     Creates a spotify session object with mocked dependencies
    """
    mocker.patch('diversify.session.spotipy.Spotify.current_user')
    mocked_get_session = mocker.patch('diversify.session._get_session')
    mock_token = Mock()
    mocked_get_session.return_value = spt.Spotify(auth=mock_token)
    return SpotifySession()


def audio_features(song_id=None):
    if song_id is None:
        song_id = fake.pyint()

    features = {}
    features['id'] = song_id
    features['speechiness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['valence'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['mode'] = int(fake.pybool())
    features['liveness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['key'] = fake.pyint(min_value=0.0, max_value=1.0)
    features['danceability'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['instrumentalness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['energy'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['tempo'] = fake.pyfloat(min_value=50.0, max_value=150.0)
    features['loudness'] = fake.pyfloat(min_value=-60.0, max_value=1.0)
    features['acousticness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    return features


def song_metadata():
    song_meta = {}
    song_meta['id'] = fake.pyint()
    song_meta['name'] = " ".join(fake.words())
    song_meta['popularity'] = fake.pyint(min_value=0, max_value=100)
    song_meta['duration_ms'] = fake.pyint()
    song_meta['album'] = " ".join(fake.words(nb=2))
    song_meta['artist'] = fake.name()
    song_meta['artist_id'] = fake.pyint()
    return song_meta


def paginated_object(values):
    for value in values[:-1]:
        result = {
            'value': value,
            'next': 'stub'
        }
        yield result
    # The last page has a null field
    yield {'value': values[-1],
           'next': None}


# ------  Tests  -------


@patch('diversify.utils.cached_token')
def test_get_session_cached_token(mock_cached_token):
    # WHEN: _get_session is called with authenticate=False
    result = _get_session(authenticate=False)
    # THEN: a Spotify object is returned
    assert isinstance(result, spt.Spotify)
    # with a token from the cache
    assert mock_cached_token.called


@patch('diversify.utils.login_user')
def test_get_session_from_api(mock_login_user):
    # WHEN: _get_session is called with authenticate=True
    result = _get_session()
    # THEN: a Spotify object is returned
    assert isinstance(result, spt.Spotify)
    # with a token from the Spotify API instead
    assert mock_login_user.called


@patch('diversify.session.spotipy.Spotify.next')
def test_session_for_all(mocked_next, spotify_session):
    # GIVEN: a paginated json response from the api
    initial_values = list(range(10))
    pages = paginated_object(initial_values)
    first_page = next(pages)
    # and a parser function that returns a list
    double_it = (lambda json: [2 * json['value']])
    # the next function gets the next page from API
    mocked_next.side_effect = (lambda json_page: next(pages))

    # When _for_all is called
    result = spotify_session._for_all(first_page, double_it)

    # THEN: the result should be all the pages' values gathered
    # into a list
    assert result == [2 * value for value in initial_values]
    # and next is called for every page except the last
    assert mocked_next.call_count == len(initial_values) - 1


# This test is kinda unecessary, since it mostly uses
# the DictWriter from the standard library
def test_write_csv_file(tmpdir, spotify_session):
    # GIVEN: A list of audiofeatures
    some_features = [audio_features() for _ in range(10)]
    # and a file path
    csv_file = tmpdir.join('test_features.csv')
    # WHEN: write csv is called
    spotify_session._write_csv(some_features, str(csv_file))

    contents = csv_file.readlines()
    # THEN: the contents should be written to file
    assert len(some_features) + 1 == len(contents)
    # with a csv header of the feature fields
    assert contents[0].rstrip('\n') == ",".join(_fields)


def test_filter_audio_features():
    # GIVEN: a list of audio features
    some_features = [audio_features() for _ in range(10)]
    for audio_feat in some_features:
        audio_feat['stub'] = 'testing'
        audio_feat['some_other'] = 'feature'

    # WHEN: filter audio features is called
    gen = SpotifySession._filter_audio_features(some_features)
    result = list(gen)

    # THEN: the unwanted features should be removed
    assert result[0].get('stub') is None
    assert result[0].get('some_other') is None


@patch('diversify.session.spotipy.Spotify.audio_features')
def test_session_get_features(mocked_audio_features, spotify_session):
    # GIVEN: a spotify session and a list of spotify
    # tracks
    songs = [song_metadata() for _ in range(20)]
    mocked_audio_features.side_effect = (lambda songs: [audio_features(song_id) for song_id in songs])

    # WHEN: get_features is called
    features = spotify_session.get_features(songs)

    # Then a list of audio features is returned for each song
    assert all([song['id'] == audio_feat['id'] for song, audio_feat in zip(songs, features)])
    # and the api is called twice, since the limit is 10
    assert mocked_audio_features.call_count == 2


@pytest.mark.skip(reason="still dont know how to generate base64 id from faker")
def test_get_features_should_raise_if_limit_too_high(spotify_session):
    # GIVEN: a spotify session and a list of spotify tracks
    songs = [song_metadata() for _ in range(30)]

    # WHEN: get_features is called with a high limit
    features = spotify_session.get_features(songs, limit=101)


@patch('diversify.session.SpotifySession._for_all')
@patch('diversify.session.spotipy.Spotify.current_user_saved_tracks')
def test_get_favorite_songs(
        mocked_saved_tracks,
        mocked_for_all,
        spotify_session):
    songs = [song_metadata() for _ in range(20)]
    songs_po = paginated_object(songs)
    first_page = next(songs_po)
    
    mocked_saved_tracks.side_effect = (lambda limit: first_page)
    result = spotify_session.get_favorite_songs()

    # THEN: All of the pages with saved user songs should be gathered
    assert result == mocked_for_all.return_value
    # for all should be called with get_song_info and the first page
    assert mocked_for_all.call_args == call(first_page, SpotifySession._get_song_info)
     

@patch('diversify.session.SpotifySession._for_all')
@patch('diversify.session.SpotifySession.get_features')
@patch('diversify.session.spotipy.Spotify.current_user_saved_tracks')
def test_get_favorite_songs_features(
        mocked_saved_tracks,
        mocked_get_features,
        mocked_for_all,
        spotify_session):

    # mocked_for_all.side_effect = (lambda page, func: 1)
    mocked_for_all.return_value = 1

    # WHEN: get_favorite_songs is called with features=True
    spotify_session.get_favorite_songs(features=True)

    # THEN: get_features should be called with the gathered songs
    # from the api 
    assert mocked_get_features.call_args == call(mocked_for_all.return_value)


@patch('diversify.session.SpotifySession._for_all')
@patch('diversify.session.spotipy.Spotify.user_playlists')
def test_get_user_playlists(mocked_for_all, mocked_spotipy, spotify_session):
    
    # WHEN: get_user_playlists is called
    spotify_session.get_user_playlists()

    # Then the result should be tuples with name of the playlist and song_metadata 
