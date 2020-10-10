
from typing import NamedTuple, Dict, Any, Tuple, List

# The song features has different fields than metadata
# (TypedDict would fit better here)
AudioFeatures = Dict[str, Any]
SongMetadata = Dict[str, Any]

Playlist = Tuple[str, List[SongMetadata]]
JsonObject = Dict[str, Any]


class SongWithFeatures(NamedTuple):
    """
    Currently there are two lists because to join
    both the song info and the audio features into a single
    object would require an inner join by the id of the song
    on two paginated endpoints results.

    This might be possible after I manage to implement a
    caching mechanism with sqlite.
    """
    songs: List[SongMetadata]
    features: List[AudioFeatures]
