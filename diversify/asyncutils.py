import asyncio
import aiohttp
from urllib.parse import urlparse
import time


async def gather_pages(spfy, paging_object):
    """
    Obtains all pages from a Spotify's paged object concurrently.
    The pagination object is explained in:
    https://developer.spotify.com/documentation/web-api/reference/object-model/#paging-object

    :param spfy: The Spotify Session Object
    :param paging_object: A paging object from Spotify Web API
    :return: list with the json response for all pages
    """
    limit = paging_object['limit']
    total = paging_object['total']
    url = paging_object['href']

    pages = [paging_object]
    # Limits the parallel connections to 10
    conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [
            get(spfy, session, url) for url in offset_urls(url, total, limit)
        ]

        rest = await asyncio.gather(*tasks)
        pages.extend(rest)
    return pages


async def get(spfy, session, url):
    """
    Makes a request to the Spotify API with the appropriate
    OAuth headers.

    :return: the json object for the response
    """
    headers = {
        **spfy._auth_headers(),
        "Content-type": "application/json"
    }

    async with session.get(url, headers=headers) as resp:
        response = await resp.json()
        return response


def offset_urls(url, total, limit):
    """
    Adds the necessary query parameters to get paginated objects with
    appropriate offsets.

    This implementation jumps the first page because the first
    request will be done by the spotipy library.

    :return: iterator with offset urls for all pages except the first
    """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    # Goes through all the offsets, starting from the limit
    # So it jumps the first page
    for i in range(limit, total, limit):
        offset_url = base_url + f'?offset={i}&limit={limit}'
        yield offset_url


if __name__ == '__main__':
    """
        Comparison between synchronous and asynchronous execution.
        *** 
        This is not comparing it anymore, since both implementation are actually using
        the paginator
        ***
    """
    from interfacespfy import SpotifySession
    import time

    spfy = SpotifySession("belzedu")

    start = time.perf_counter()
    teste = spfy._session.current_user_saved_tracks(50)
    paginator = asyncio.run(gather_pages(spfy._session, teste))
    result = paginator.run()

    async_data = []
    for json in result:
        parsed = SpotifySession._get_song_info(json)
        async_data.extend(parsed)

    async_time = time.perf_counter() - start
    print(f'Asynchronous time: {async_time}')
    print(f'async size: {len(async_data)}')

    start = time.perf_counter()
    sync_data = spfy.get_favorite_songs()
    sync_time = time.perf_counter() - start
    print(f'Synchronous time: {sync_time}')
    print(f'sync size: {len(sync_data)}')
