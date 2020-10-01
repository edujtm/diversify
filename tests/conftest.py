import pytest


@pytest.fixture()
def spotify_env(monkeypatch):
    client_id = 'test-client-id-123456'
    client_secret = 'test-secret-key-456789'
    redirect_uri = 'https://edujtm.github.io/diversify/redirect'
    monkeypatch.setenv('SPOTIPY_CLIENT_ID', client_id)
    monkeypatch.setenv('SPOTIPY_CLIENT_SECRET', client_secret)
    monkeypatch.setenv('SPOTIPY_REDIRECT_URI', redirect_uri)
    return client_id, client_secret, redirect_uri

