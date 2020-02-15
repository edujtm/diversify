import os
import tempfile

CACHE_FILE = os.path.join(tempfile.gettempdir(), ".cache-diversify")

SCOPE = ['user-library-read', 'playlist-modify-private']