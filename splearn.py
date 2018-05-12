import numpy as np


class MLP:
    def __init__(self, *args):
        """
        Construtor do multilayer perceptron.

        O argumento args indica o tamanho de cada camada da rede neural. Sendo interpretado de acordo com o

        :param args: Any iterable, int or package of int (like a unpacked array Ex: *array)
        """
        self._network = None
        try:
            self.start_parameters(args[0])
        except TypeError:
            try:
                if len(args) == 1:
                    neuron_sizes = [args[0] for _ in range(args[0])]
                    self.start_parameters(neuron_sizes)
                elif len(args) == 2:
                    neuron_sizes = [args[1] for _ in range(args[0])]
                    self.start_parameters(neuron_sizes)
                else:
                    self.start_parameters(args)
            except TypeError:
                raise TypeError("Invalid argument for constructor. Expected: int, pair of int or iterable of ints.")
        self._input = []
        self._output = []
        self._gradient = []

    def start_parameters(self, neuron_sizes):
        """
        Inicializa o vetor de valores z (saida de cada neuronio sem ativaçao) e dos valores y (valores apos a
        ativacao) com valores 0.0 iniciais.

        :param neuron_sizes:
        :return:
        """
        self._network = [np.zeros(value) for value in neuron_sizes]
        self.start_weights()

    def start_weights(self):
        """
        Inicializa a matriz de pesos para cada neuronio
        :return:
        """
        pass

    def _test(self):
        print(self._network)

    # --- interface ---
    def predict(self, sample):
        """
           Essa funcao e o forward. Ela recebe uma vetor de amostras (uma musica no caso do projeto da unidade 1) e aplica na
           rede neural, mas nao faz o backpropagation, apenas retorna o vetor resultante.

        :param sample:
        :return: Um valor indicando se a pessoa gosta ou nao da musica (caracteristicas da musica)
        """
        """ 
        O algoritmo e assim:
        - Faz o somatorio para cada neuronio em self.network
        - Aplica a funcao de ativacao em cada resultado do somatorio e salva em network na camada n 
        - Repete isso ate chegar na ultima camada
        - Os valores da ultima camada de activated serao o resultado
        """
        pass

    def fit(self, data):
        bias = -1
        """
        - para cada amostra em data:
        - Aplica predict
        - com o resultado de predict, calcula backpropagation
        """
        pass

    # --- calculations ---
    def _backprop(self, expected):
        """
        Implementa backpropagation
        :param expected: Valor da resposta desejada da amostra calculada
        :return:
        """
        pass

    def activate(self, value):
        """
        Implementa a funçao de ativaçao
        :param value:
        :return:
        """
        pass

    def neuron_sum(self, layer, neuron):
        pass

    def gradient(self, layer):
        pass

    # --- modifiers ---
    def append(self):
        pass
