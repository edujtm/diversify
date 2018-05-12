
import numpy as np

class MLP:
    def __init__(self, *args):
        """
        Construtor do multilayer perceptron.

        O argumento args indica o tamanho de cada camada da rede neural. Sendo interpretado de acordo com o

        :param args: Any iterable, int or package of int (like a unpacked array Ex: *array)
        """
        try:
            if len(args[0]) == 2:
                self.start_parameters(args[0])
            else:
                self._network = [[0.0] * value for value in args[0]]
        except TypeError:
            try:
                if len(args) == 1:
                    self._network = [[0.0] * args[0] for _ in range(args[0])]
                elif len(args) == 2:
                    self._network = [[0.0] * args[1] for _ in range(args[0])]
                else:
                    self._network = [[0.0] * value for value in args]
            except TypeError:
                raise TypeError("Invalid argument for constructor. Expected: int, pair of int (tuple or list) or "
                                "sequence of ints")
        self._input = []
        self._output = []
        # matrix de pesos para cada neuronio
        self._weight = []
        self._activated = []

    def start_parameters(self, neuron_sizes):
        """
        Inicializa o vetor de valores z (saida de cada neuronio sem ativaçao) e dos valores y (valores apos a
        ativacao) com valores 0.0 iniciais.

        :param neuron_sizes:
        :return:
        """
        if len(neuron_sizes) == 1:
            self._network = [np.zeros(neuron_sizes[0]) for _ in range(neuron_sizes[0])]
        elif len(neuron_sizes) == 2:
            self._network = [np.zeros(neuron_sizes[1]) for _ in range(neuron_sizes[0])]
        else:
            self._network = [np.zeros(value) for value in neuron_sizes]
        self.start_weights()


    def start_weights(self):
        pass

    def _test(self):
        print(self._network)


    # --- interface ---
    def predict(self, data):
        pass

    def fit(self, data):
        bias = -1
        # Faz o somatorio para cada neuronio em self.network
        # Salva o resultado na matriz self.network pois vai precisar no backpropagation
        # Aplica a funcao de ativacao em cada resultado do somatorio e salva em activated
        pass

    # --- calculations ---
    def _backprop(self):
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


    # --- modifiers ---
    def append(self):
        pass