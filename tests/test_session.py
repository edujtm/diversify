from unittest.mock import Mock, patch
import pytest
from faker import Faker
import spotipy as spt
from diversify.session import SpotifySession, _get_session, _fields

fake = Faker()
Faker.seed(0)

# ------  Fixtures  -------


@pytest.fixture()
def mocked_spotify_session(mocker):
    """
     Creates a spotify session object with mocked dependencies
    """
    mocker.patch('diversify.session.spotipy.Spotify.current_user')
    mocked_get_session = mocker.patch('diversify.session._get_session')
    mock_token = Mock()
    mocked_get_session.return_value = spt.Spotify(auth=mock_token)
    return SpotifySession()


def audio_features():
    features = {}
    features['id'] = fake.pyint()
    features['speechiness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['valence'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['mode'] = int(fake.pybool())
    features['liveness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['key'] = fake.pyint(min_value=0.0, max_value=1.0)
    features['danceability'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    features['loudness'] = fake.pyfloat(min_value=-60.0, max_value=1.0)
    features['acousticness'] = fake.pyfloat(min_value=0.0, max_value=1.0)
    return features


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
def test_session_for_all(mocked_next, mocked_spotify_session):
    # GIVEN: a paginated json response from the api
    initial_values = list(range(10))
    pages = paginated_object(initial_values)
    first_page = next(pages)
    # and a parser function that returns a list
    double_it = (lambda json: [2 * json['value']])
    # the next function gets the next page from API
    mocked_next.side_effect = (lambda json_page: next(pages))

    # When _for_all is called
    result = mocked_spotify_session._for_all(first_page, double_it)

    # THEN: the result should be all the pages' values gathered
    # into a list
    assert result == [2 * value for value in initial_values]
    # and next is called for every page except the last
    assert mocked_next.call_count == len(initial_values) - 1


# This test is kinda unecessary, since it mostly uses
# the DictWriter from the standard library
def test_write_csv_file(tmpdir, mocked_spotify_session):
    # GIVEN: A list of audiofeatures
    some_features = [audio_features() for _ in range(10)]
    # and a file path
    csv_file = tmpdir.join('test_features.csv')
    # WHEN: write csv is called
    mocked_spotify_session._write_csv(some_features, str(csv_file))

    contents = csv_file.readlines()
    # THEN: the contents should be written to file
    assert len(some_features) + 1 == len(contents)
    # with a csv header of the feature fields
    assert contents[0].rstrip('\n') == ",".join(_fields)

