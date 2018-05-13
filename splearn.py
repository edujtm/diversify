import numpy as np


class NotFittedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AlreadyFittedError(Exception):
    def __init__(self, message):
        super().__init__(message)


def activate(value):
    """
    Implementa a funçao de ativaçao
    :param value:
    :return:
    """
    return 1 / (1 + np.exp(-value))


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
            self.neuron_sizes = []
            for value in args[0]:
                self.neuron_sizes.append(value)
        except TypeError:
            try:
                if len(args) == 1:
                    self.neuron_sizes = [args[0] for _ in range(args[0])]
                elif len(args) == 2:
                    self.neuron_sizes = [args[0] for _ in range(args[1])]
                else:
                    self.neuron_sizes = args
            except TypeError:
                raise TypeError("Invalid argument for constructor. Expected: int, pair of int or iterable of ints.")

    def _start_parameters(self, inputsize, outputsize):
        """
        Inicializa a matriz de pesos para cada neuronio assim como as matriz de saidas y dos neuronios
        :return: None
        """

        # inicializando camadas de saidas da rede neural (cada camada possui um vetor de saida)
        # Primeira camada de input
        # camadas internas definidas por neuron_sizes
        # Ultima camada e output
        self._network = [np.zeros(shape=(inputsize, 1))]
        self._network.extend([np.zeros(shape=(value, 1)) for value in self.neuron_sizes])
        self._network.append(np.zeros(shape=(outputsize, 1)))

        # inicializando pesos
        self._weights = []
        domain = 4 * np.sqrt(6 / (inputsize + outputsize))

        # Cria camada de pesos de entrada
        shape = (len(self._network[0]), inputsize + 1)
        self._weights.append(np.random.uniform(-domain, domain, size=shape))

        # Cria camadas de pesos ocultas
        for i in range(1, len(self._network) - 1):
            shape = (len(self._network[i + 1]), len(self._network[i]) + 1)
            self._weights.append(np.random.uniform(-domain, domain, size=shape))

    def _test(self):
        print(self._network)

    # --- interface ---
    def predict(self, data):
        """
        Essa funcao e o forward. Ela recebe uma vetor de amostras (uma musica no caso do projeto da unidade 1) e
        aplica na rede neural, mas nao faz o backpropagation, apenas retorna o vetor resultante.

        :param data:
        :return: Um valor indicando se a pessoa gosta ou nao da musica (caracteristicas da musica)
        """
        if not self.fitted:
            raise NotFittedError("Neural network is unfitted. Try passing the data matrix to fit() method")

        try:
            # Tenta classificar uma matriz dados
            classification = [self._forward(sample) for sample in data]
            return classification
        except TypeError:
            # Se nao forem varios dados, assume que seja apendas um array de dados
            return [self._forward(data)]

    def fit(self, data, target):
        """
        - para cada amostra em data:
        - Aplica predict
        - com o resultado de predict, calcula backpropagation
        """
        inputsize = data.shape[1]
        outputsize = data.shape[1]
        if not self.fitted:
            self._start_parameters(inputsize, outputsize)
            self.fitted = True

        """
        for sample, expected in zip(data, target):
            # TODO implement backprop function
            self.predict(sample)
            self._backprop(expected)
        """
        return self

    # --- calculations ---

    def _forward(self, sample):
        temp = sample.copy()
        temp.resize(len(sample), 1)

        np.copyto(self._network[0], temp)

        print(range(len(self._network)))
        for i in range(len(self._network) - 1):
            print(i)
            extended = self._network[i].copy()
            # Add bias to input
            bias = np.array([[-1]])
            extended = np.append(extended, bias, axis=0)

            # Calcula saida do proximo neuronio fazendo y(k) = W(k-1) * y(k-1)
            z = self._weights[i].dot(extended)
            self._network[i + 1] = np.apply_along_axis(activate, 1, z)
            # Retorna a ultima camada que representa o output
        return self._network[-1]

    def _backprop(self, expected):
        """
        Implementa backpropagation
        :param expected: Valor da resposta desejada da amostra calculada
        :return:
        """

        pass

    def gradient(self, layer):
        pass

    # --- modifiers ---

    def append(self, layer):
        if self.fitted:
            raise AlreadyFittedError("Cannot change network layout after fitting data. Try creating a new mlp network.")
        pass

    def pop(self, layer):
        pass

    def resize(self, layer, size):
        pass

    def set_step(self, new_step):
        self._step = new_step

    # --- helpers ---

    def describe(self):
        if not self.fitted:
            print("Unfitted MLP network for regression with {0} hidden layers.".format(len(self.neuron_sizes)))
            print("Input and output layers will be deduced from data matrix")
            print("Number of neurons in hidden layer:")
            for size, idx in enumerate(self.neuron_sizes):
                print("layer {0} size: {1}".format(idx, size))
            return
