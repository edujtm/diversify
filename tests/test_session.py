from unittest.mock import Mock, patch
import pytest
import spotipy as spt
from diversify.session import SpotifySession, _get_session


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

