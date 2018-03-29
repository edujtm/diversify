import random
import pandas as pd
import numpy as np
import pprint

tam_populacao = 20
tam_genes = 20
taxa_crossover = 0.7
maxiter = 50

_user1 = None       # Lista de musicas do primeiro usuario
_user2 = None       # Lista de musicas do segundo usuario
_nsongs = None      # Lista de musicas aleatorias
_twousers = False

def gerar_individuo():
    each = tam_genes // 4 if _twousers else tam_genes // 2
    alreadyplaced = 2 * each if _twousers else each

    music1 = np.random.choice(_user1, each)
    music2 = []
    if _twousers:
        music2 = np.random.choice(_user2, each)

    ransongs = np.random.choice(_nsongs, (tam_genes - alreadyplaced))
    return music1.tolist() + music2.tolist() + ransongs.tolist()


def gerar_populacao():
    populacao = []
    for i in range(tam_populacao):
        populacao.append(gerar_individuo()) #adiciona o individuo gerado na populacao no final da lista
    return populacao


def fitness(playlist):
    result = correlation(playlist, _user1)
    if _twousers:
        result += correlation(playlist, _user2)
        result /= 2
    return result


def correlation(indv1, indv2):
    frame1 = pd.DataFrame(indv1).select_dtypes(include=['float64', 'int64']) # Filtra o individuo para ficar apenas com valores int ou float
    frame2 = pd.DataFrame(indv2).select_dtypes(include=['float64', 'int64'])
    result = frame1.corrwith(frame2.set_index(frame1.index))
    return result.sum()


def selecionar_pais(populacao, k=3):
    pais = []

    for torneio in range(len(populacao)):

        competidores = [random.choice(populacao) for i in range(k)]

        maior_avaliacao = fitness(competidores[0])
        vencedor = competidores[0]
        for i in range(1, k):
            avaliacao = fitness(competidores[i])
            if avaliacao > maior_avaliacao:
                maior_avaliacao = avaliacao
                vencedor = competidores[i]

        pais.append(vencedor)

    return pais


def gerar_filhos(pais):
    nova_populacao = []

    for i in range(tam_populacao//2): #2 pais geram 2 filhos

        pai1 = random.choice(pais)
        pai2 = random.choice(pais)

        if random.random() < taxa_crossover:
            corte = random.randint(1, len(pai1)-1)
            filho1 = pai1[0:corte] + pai2[corte:]
            filho2 = pai2[0:corte] + pai1[corte:]
            nova_populacao.append(filho1)
            nova_populacao.append(filho2)
        else:
            nova_populacao.append(pai1)
            nova_populacao.append(pai2)

    return nova_populacao


def mutacao(indv, prob):
    if np.random.random() < prob:
        result = indv[::2]
        result.extend(np.random.choice(_nsongs, len(indv) // 2))
        print("mutation -", len(result))
        return result
    return indv


def run():
    pop = gerar_populacao()

    for iter in range(maxiter):
        pais = selecionar_pais(pop)
        filhos = gerar_filhos(pais)
        pop = [mutacao(filho, 0.01) for filho in filhos]

    return pop


def start(user1, nsongs, user2=None):
    global _user1, _nsongs, _twousers, _user2
    _user1 = user1
    _nsongs = nsongs

    if user2 is not None:
        _twousers = True
        _user2 = user2

    pop = run()
    return pop[0]


if __name__ == '__main__':
    import interfacespfy as isp
    #populacao = gerar_populacao(tam_populacao)
    #pais = selecionar_pais(populacao, tam_populacao, k)
    #nova_populacao = gerar_filhos(pais, tam_populacao, taxa_crossover)

    indv1 = pd.read_csv('csvfiles/playlistfeatures.csv')
    indv2 = pd.read_csv('csvfiles/maxmyllercarvalhofeatures.csv')

    #pprint.pprint(indv1)
    #pprint.pprint(indv2)

    spfy = isp.login_user('belzedu')

    _user1 = indv1.to_dict('records')[:tam_genes]
    _user2 = indv2.to_dict('records')[:tam_genes]
    _twousers = True

    #pprint.pprint(_user1)
    #pprint.pprint(_user2)

    seeds = np.random.choice(_user1, 2).tolist() + np.random.choice(_user2, 2).tolist()
    nsongs = isp.get_new_songs(spfy, seeds, limit=90)
    _nsongs = isp.get_features(spfy, nsongs, limit=50)
    #pprint.pprint(_nsongs)
    result = start(_user1, user2=_user2, nsongs=_nsongs)

    pprint.pprint(result)
    """
    pop = gerar_populacao()
    #pprint.pprint(pop[0])
    pais = selecionar_pais(pop)
    #pprint.pprint(pais[0])
    filhos = gerar_filhos(pais)
    #pprint.pprint(filhos[0])
    result = [mutacao(filho, 0.01) for filho in filhos]
    pprint.pprint(result[0])
    """
    '''
    for i in range(tam_populacao):
        print(populacao[i])
    '''
