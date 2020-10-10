import warnings
import random
import pandas as pd
import numpy as np
import pprint
import click

from diversify.session import SpotifySession

warnings.simplefilter(action='ignore', category=FutureWarning)

population_size = 20
genes_size = 20
crossover_rate = 0.7
maxiter = 50

_columns = ['speechiness', 'liveness', 'danceability', 'loudness', 'acousticness',
            'instrumentalness', 'energy', 'tempo']

_user1 = None  # Music list for first user
_user2 = None  # Music list for second user
_nsongs = None  # Random music list for mutations
_twousers = False


def generate_individual():
    each = genes_size // 4 if _twousers else genes_size // 2
    alreadyplaced = 2 * each if _twousers else each

    music1 = _user1.sample(each)

    ransongs = _nsongs.sample(genes_size - alreadyplaced)
    result = music1.append(ransongs)
    if _twousers:
        music2 = _user2.sample(each)
        result = result.append(music2)

    return result


def generate_population():
    return [generate_individual() for i in range(population_size)]


def fitness(playlist):
    result = correlation(playlist, _user1)
    if _twousers:
        result += correlation(playlist, _user2)
        result /= 2
    return result


def correlation(indv1, indv2):
    # Filtra o individuo para ficar apenas com valores int ou float
    frame1 = indv1.select_dtypes(include=['float64', 'int64'])
    frame2 = indv2.select_dtypes(include=['float64', 'int64'])
    result = frame1.corrwith(frame2.set_index(frame1.index))
    return result.sum()


def select_parents(population, k=3):
    parents = []
    for tournament in range(len(population)):
        competitors = [random.choice(population) for i in range(k)]
        winner = max(competitors, key=fitness)
        parents.append(winner)
    return parents


def remove_duplicates(indv):
    result = indv.drop_duplicates(keep='first')
    all_data = _user1.append(_nsongs)

    if _twousers:
        all_data.append(_user2)

    while len(result.index) != 20:
        songs = all_data.sample(population_size - len(result.index))
        result = result.append(songs)
        result.drop_duplicates(keep='first', inplace=True)
    return result


def generate_children(parents):
    new_population = []

    for i in range(population_size // 2):  # 2 parents generate 2 children

        parent1 = random.choice(parents)
        parent2 = random.choice(parents)

        if random.random() < crossover_rate:
            cut = random.randint(1, len(parent1) - 1)
            child1 = parent1.sample(cut).append(parent2.sample(genes_size - cut))
            child2 = parent2.sample(cut).append(parent1.sample(genes_size - cut))
            child1 = remove_duplicates(child1)
            child2 = remove_duplicates(child2)
            if not child1.index.unique or not child2.index.unique:
                new_population.extend([parent1, parent2])
            else:
                new_population.extend([child1, child2])
        else:
            new_population.extend([parent1, parent2])

    return new_population


def mutation(indv, prob):
    if np.random.random() < prob:
        rest = _nsongs.sample(len(indv) // 2)
        dropped = indv.drop(indv.index[::2])
        result = dropped.append(rest)
        result = remove_duplicates(result)
        # if len(result) == 20:       # Gambiarra master
        return result
    return indv


def run():
    pop = generate_population()

    with click.progressbar(range(maxiter)) as bar:
        for _ in bar:
            parents = select_parents(pop)
            children = generate_children(parents)
            pop = [mutation(child, 0.01) for child in children]

    return pop


def start(spfy, user1, user2=None):
    global _user1, _nsongs, _twousers, _user2
    _user1 = user1.set_index('id')[:genes_size][_columns]

    if user2 is not None:
        _twousers = True
        _user2 = user2.set_index('id')[:genes_size][_columns]
        samples = _user1.sample(2).append(_user2.sample(2))
    else:
        samples = _user1.sample(4)

    seeds = [{'id': value} for value in samples.index]
    nsongs = spfy.get_new_songs(seeds)
    _nsongs = pd.DataFrame(spfy.get_features(nsongs))
    _nsongs.set_index('id', inplace=True)

    pop = run()
    return max(pop, key=fitness)


if __name__ == '__main__':
    from argparse import ArgumentParser, RawTextHelpFormatter

    description_hint = """
        This is a sample program for the diversify playlist generator.
        It will create a new playlist in your account based on some sample
        data from the creators of this app.
        
        The app will redirect you to a page in your browser,
        where you will be asked to login into your spotify account.
        
        After logging in into your account, you should be redirected to a page
        with the URL pattern as follows:
        
        http://localhost/?code={code-pattern}
        
        where you should copy the code-pattern and paste into your terminal. 
        These steps are only necessary once and are a current limitation of the
        spotify WEB API.
        
        If you prefer, you can also log in through the spotify website into your 
        browser and then run this program, which will not ask for your credentials
        as you'll be already logged in.
        
        Spotify website: https://www.spotify.com/
    """

    parser = ArgumentParser(prog='python3 genetic.py',
                            description=description_hint, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p', '--playlist_name', nargs='+', default=['Genetic playlist'],
                        help='The name for the playlist that will be created')

    args = parser.parse_args()

    pl_name = ' '.join(args.playlist_name)

    indv1 = pd.read_csv('csvfiles/playlistfeatures.csv')
    indv2 = pd.read_csv('csvfiles/maxmyllercarvalhofeatures.csv')

    spfy = SpotifySession()

    _user1 = indv1[:genes_size][_columns + ['id']]
    _user2 = indv2[:genes_size][_columns + ['id']]
    _twousers = True

    print(_columns)

    result = start(spfy, _user1, user2=_user2)

    pprint.pprint(result)
    resultids = result.index.tolist()
    spfy.tracks_to_playlist(trackids=resultids, name=pl_name)
