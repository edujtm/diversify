import numpy as np

class NotFittedError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors

class MLP:
    def __init__(self, *args):
        """
        Construtor do multilayer perceptron.

        O argumento args indica o tamanho de cada camada da rede neural. Sendo interpretado de acordo com o

        :param args: Any iterable, int or package of int (like a unpacked array Ex: *array)
        """
        self._network = None
        self._weights = None
        self._step = 0.5
        self._sizes = None
        self.fitted = False

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

    def start_parameters(self, neuron_sizes):
        """
        Inicializa o vetor de valores z (saida de cada neuronio sem ativaçao) e dos valores y (valores apos a
        ativacao) com valores 0.0 iniciais.

        :param neuron_sizes:
        :return:
        """
        self._network = [np.zeros(value) for value in neuron_sizes]

    def start_weights(self, inputsize, outputsize):
        """
        Inicializa a matriz de pesos para cada neuronio
        :return:
        """
        self._weights = []
        domain = 4 * np.sqrt(6 / (inputsize + outputsize))

        # Cria camada de entrada
        shape = (inputsize+1, len(self._network[0]))
        self._weights.append(np.random.uniform(-domain, domain, size=shape))

        # Cria camadas ocultas
        for i in range(len(self._network)-1):
            shape = (len(self._network[i+1]), len(self._network[i]+1))
            self._weights.append(np.random.uniform(-domain, domain, size=shape))
        shape = (len(self._network[-1])+1, outputsize)

        # Cria camada de saida
        self._weights.append(np.random.uniform(-domain, domain, size=shape))

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
        if self.fitted:
            pass
        else:
            raise NotFittedError("Neural network is unfitted. Try passing the data matrix to fit() method")

    def fit(self, data, target):
        """
        - para cada amostra em data:
        - Aplica predict
        - com o resultado de predict, calcula backpropagation
        """
        self.fitted = True
        inputsize = data.shape[0]
        outputsize = len(np.unique(target))
        self.start_weights(inputsize, outputsize)

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
        bias = -1
        pass

    def gradient(self, layer):
        pass

    # --- modifiers ---
    def append(self, layer):
        pass

    def set_step(self, new_step):
        self._step = new_step