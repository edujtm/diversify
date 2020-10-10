import os
import tempfile
from pathlib import Path

CACHE_FILE = os.path.join(tempfile.gettempdir(), ".cache-diversify")

SCOPE = ['user-library-read', 'playlist-modify-private']

DIVERSIFY_FOLDER = Path.home() / '.config/diversify'
