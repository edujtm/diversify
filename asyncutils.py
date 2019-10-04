import asyncio
import aiohttp
from urllib.parse import urlparse
import time

from dotenv import load_dotenv

load_dotenv()


class AsyncPaginator:
    def __init__(self, spfy, paging_object):
        """
            This class tries to make the requests for pagination objects
            from the Spotify Web API asynchronously.

        :param spfy: The Spotipy Session Object
        :param paging_object: A Paging Object from Spotify Web API
        """
        self.paging = paging_object
        self.limit = paging_object['limit']
        self.total = paging_object['total']
        # self.executor = futures.ThreadPoolExecutor(10)
        self.spfy = spfy
        self.loop = asyncio.get_event_loop()

    def run(self):
        # The first request is made synchronously to get the base url
        # meaning self.paging is already a result of a request
        first = [self.paging]

        rest = self.loop.run_until_complete(self.get_all_data(self.paging['href']))

        first.extend(rest)
        return first

    async def get_all_data(self, url):
        # Extracts the base_url from the pagination data from spotify API
        old_url = urlparse(url)
        base_url = old_url.scheme + '://' + old_url.netloc + old_url.path

        # A Little hack here: This is the necessary header from the spotipy.Spotify object
        # I'm doing this only because the spotipy library isn't asynchronous

        session = aiohttp.ClientSession()
        tasks = []
        for i in range(self.limit, self.total, self.limit):
            full_url = base_url + f'?offset={i}&limit={self.limit}'
            tasks.append(self.get(session, full_url))

        result = await asyncio.gather(*tasks)

        await session.close()
        return result

    async def get(self, session, url):
        headers = {**self.spfy._auth_headers(), 'Content-type': 'application/json'}

        async with session.get(url, headers=headers) as resp:
            response = await resp.json()
            return response


if __name__ == '__main__':
    """
        Comparison between synchronous and asynchronous execution.
    """
    from interfacespfy import SpotifySession

    spfy = SpotifySession("belzedu")

    start = time.perf_counter()
    teste = spfy._session.current_user_saved_tracks(50)
    paginator = AsyncPaginator(spfy._session, teste)
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
