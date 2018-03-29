import random
import pandas as pd
import numpy as np
import interfacespfy as isp
import pprint

tam_populacao = 20
tam_genes = 20
taxa_crossover = 0.7
maxiter = 50

_columns = ['speechiness', 'liveness', 'danceability', 'loudness', 'acousticness',
           'instrumentalness', 'energy', 'tempo']

_user1 = None       # Lista de musicas do primeiro usuario
_user2 = None       # Lista de musicas do segundo usuario
_nsongs = None      # Lista de musicas aleatorias
_twousers = False

def gerar_individuo():
    each = tam_genes // 4 if _twousers else tam_genes // 2
    alreadyplaced = 2 * each if _twousers else each

    music1 = _user1.sample(each)
    music2 = []
    if _twousers:
        music2 = _user2.sample(each)

    ransongs = _nsongs.sample(tam_genes - alreadyplaced)
    return music1.append(music2).append(ransongs)


def gerar_populacao():
    return [gerar_individuo() for i in range(tam_populacao)]


def fitness(playlist):
    result = correlation(playlist, _user1)
    if _twousers:
        result += correlation(playlist, _user2)
        result /= 2
    return result


def correlation(indv1, indv2):
    frame1 = indv1.select_dtypes(include=['float64', 'int64']) # Filtra o individuo para ficar apenas com valores int ou float
    frame2 = indv2.select_dtypes(include=['float64', 'int64'])
    result = frame1.corrwith(frame2.set_index(frame1.index))
    return result.sum()


def selecionar_pais(populacao, k=3):
    pais = []
    for torneio in range(len(populacao)):
        competidores = [random.choice(populacao) for i in range(k)]
        #for comp in competidores:
        #   print('pai -', len(comp))
        vencedor = max(competidores, key=fitness)
        pais.append(vencedor)
    return pais


def remove_duplicates(indv):
    result = indv.drop_duplicates(keep='first')
    subs = np.random.choice([_user1, _user2, _nsongs])
    while len(result.index) != 20:
        songs = subs.sample(tam_populacao - len(result.index))
        result = result.append(songs)
        result.drop_duplicates(keep='first', inplace=True)
    return result

def gerar_filhos(pais):
    nova_populacao = []

    for i in range(tam_populacao//2): #2 pais geram 2 filhos

        pai1 = random.choice(pais)
        pai2 = random.choice(pais)

        if random.random() < taxa_crossover:
            corte = random.randint(1, len(pai1)-1)
            filho1 = pai1.sample(corte).append(pai2.sample(tam_genes-corte))
            filho2 = pai2.sample(corte).append(pai1.sample(tam_genes-corte))
            filho1 = remove_duplicates(filho1)
            filho2 = remove_duplicates(filho2)
            if not filho1.index.unique or not filho2.index.unique:
                nova_populacao.extend([pai1, pai2])
            else:
                nova_populacao.extend([filho1, filho2])
        else:
            nova_populacao.extend([pai1, pai2])

    return nova_populacao


def mutacao(indv, prob):
    if np.random.random() < prob:
        rest = _nsongs.sample(len(indv) // 2)
        dropped = indv.drop(indv.index[::2])
        result = dropped.append(rest)
        print('mutation -', len(result))
        result = remove_duplicates(result)
        #if len(result) == 20:       # Gambiarra master
        return result
    return indv


def run():
    pop = gerar_populacao()

    for iter in range(maxiter):
        print(iter)
        pais = selecionar_pais(pop)
        filhos = gerar_filhos(pais)
        pop = [mutacao(filho, 0.01) for filho in filhos]

    return pop


def start(spfy, user1, user2=None):
    global _user1, _nsongs, _twousers, _user2
    _user1 = user1.set_index('id')[:tam_genes][_columns]

    if user2 is not None:
        _twousers = True
        _user2 = user2.set_index('id')[:tam_genes][_columns]

    samples = _user1.sample(2).append(_user2.sample(2))
    seeds = [{'id': value} for value in samples.index]
    nsongs = isp.get_new_songs(spfy, seeds, limit=90)
    _nsongs = pd.DataFrame(isp.get_features(spfy, nsongs, limit=50))
    _nsongs.set_index('id', inplace=True)

    pop = run()
    return max(pop, key=fitness)


if __name__ == '__main__':

    indv1 = pd.read_csv('csvfiles/playlistfeatures.csv')
    indv2 = pd.read_csv('csvfiles/maxmyllercarvalhofeatures.csv')

    #pprint.pprint(indv1)
    #pprint.pprint(indv2)

    spfy = isp.login_user('belzedu')

    _user1 = indv1.set_index('id')[:tam_genes][_columns]
    _user2 = indv2.set_index('id')[:tam_genes][_columns]
    _twousers = True

    #pprint.pprint(_user1)
    #pprint.pprint(_user2)

    result = start(spfy, _user1, user2=_user2)

    pprint.pprint(result)
    resultids = result.index.tolist()
    isp.tracks_to_playlist(spfy, 'belzedu', trackids=resultids, name='First of many')
