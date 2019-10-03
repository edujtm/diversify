import numpy as np
import pprint
import pandas as pd


class NotFittedError(Exception):
    """
    Exception raised when the user tries to predict data in a neural network that's not fitted yet.
    It's used to avoid errors on the first and last layers of the multilayer perceptron, because the size
    of these layers depends on the rank (n-dimension) of the input and output data.
    """
    def __init__(self, message):
        super().__init__(message)


class AlreadyFittedError(Exception):
    """
    Raised when the user tries to modify a neural network that's already fitted
    to some data.
    """
    def __init__(self, message):
        super().__init__(message)


def load_mlearn(spfy, users):
    """
        This function joins all public playlists from the user in users into a dataframe containing the spotify id
    of the song and it's features as columns.

    It was going to be used to feed the multilayer perceptron network.

    Currently it's not usable, but it's left here because it will probably be useful in the future.

    :param spfy: The spotify WEB API client.
    :param users: A list containing the users from which the public playlists will be gathered
    :return: Training data, training labels, test data, test labels
    """
    songs = []
    feat = []
    try:
        for user in users:
            query = spfy.get_user_playlists(user, limit=10)
            userlist = []
            for playlist in query:
                featarray = spfy.get_features(playlist, limit=10)
                feat.extend(featarray)
                userlist.extend(playlist)
            songs.append((user, userlist))
    except TypeError:
        songs = spfy.get_user_playlists(spfy, users, limit=10)
        feat = spfy.get_features(spfy, songs, limit=10)

    datafeat = pd.DataFrame(feat).set_index("id")
    preferences = []
    for user, playlist in songs:
        pprint.pprint(playlist)
        musicdata = pd.DataFrame(playlist).set_index("id")
        musicdata.drop("name", axis=1, inplace=True)
        musicdata[user] = 1.0
        preferences.append(musicdata)

    dropset = ["acousticness", "danceability", "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "valence"]
    data = datafeat.join(preferences)
    data.dropna(subset=dropset, inplace=True)
    data.fillna(0.0, inplace=True)
    pprint.pprint(data)


def activate(value):
    """
    Implements sigmoid activation function
    :param value: Input to the function
    :return: Result value of sigmoid function
    """
    return 1 / (1 + np.exp(-value))


class MLP:
    def __init__(self, *args):
        """
        Multilayer perceptron constructor.

        The args argument indicates the size of each neural network layer. It's interpreted according to it's data type,
        which can be an integer or an list of integers.

        The values of the parameters are used only to the change the size of internal layers, the external layers are
        going to be defined according to the sample matrix format, when it's passed to the fit method.

        :param args: Any iterable, int or package of int (like a unpacked array Ex: *array)
        """
        self._network = None
        self._weights = None
        self._step = 0.5
        self._sizes = None
        self.fitted = False

        # TODO change this try-catch to a instanceof
        try:
            # If the user passes an iterable of integers in the first parameter, it will create the internal layers
            # with the size defined by the integer position
            self.neuron_sizes = []
            for value in args[0]:
                self.neuron_sizes.append(value)
        except TypeError:
            # If the first argument is not an iterable
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
        Starts the weight matrix for each neuron as well as the neuron's output matrix y.
        :return: None
        """

        # Initializing the neural network's activated layers (each layer has an output vector for activated values)
        # Input layer - Internal layers (defined by neuron_sizes) - Output layer
        self._network = [np.zeros(shape=(inputsize, 1))]
        self._network.extend([np.zeros(shape=(value, 1)) for value in self.neuron_sizes])
        self._network.append(np.zeros(shape=(outputsize, 1)))

        # Starts weights with xavier's initialization method
        self._weights = []
        domain = 4 * np.sqrt(6 / (inputsize + outputsize))

        # Creates the input layer weigths
        shape = (len(self._network[1]), inputsize + 1)
        self._weights.append(np.random.uniform(-domain, domain, size=shape))

        # Instantiates the internal layer weigths
        for i in range(1, len(self._network) - 1):
            shape = (len(self._network[i + 1]), len(self._network[i]) + 1)
            self._weights.append(np.random.uniform(-domain, domain, size=shape))

    def _test(self):
        print(self._network)

    # --- interface ---
    def predict(self, data):
        """
            Implements the forward passing of the neural network. It receives a sample vector and applies it to the
        network, but it doesn't do backpropagation of the data, only returning the resulting vector.

        :param data: An numpy matrix in which each line is a data sample
        :return: An numpy matrix with the sample predictions
        """
        if not self.fitted:
            raise NotFittedError("Neural network is unfitted. Try passing the data matrix to fit() method")

        try:
            # Assumes data is composed of various data samples
            results = [self._forward(sample).ravel() for sample in data]
            classification = np.vstack(results)
            return classification
        except TypeError:
            # If it's not, assumes it's only one data sample
            return [self._forward(data)]

    def fit(self, data, target):
        """
            Train the neural network using the dataset in data. It uses the backpropagation algorithm
            with sigmoid activation functions to introduce non-linearities.

        :param data: Numpy array containing data samples used as input for the network
        :param target: Numpy array containing the desired value for each sample
        :return: The class itself for method chaining
        """
        inputsize = data.shape[1]
        outputsize = target.shape[1]

        if not self.fitted:
            self._start_parameters(inputsize, outputsize)
            self.fitted = True

        for sample, expected in zip(data, target):
            self.predict(sample)
            self._backprop(expected)
        return self

    # --- calculations ---

    def _forward(self, sample):
        """
            Calcula os resultados dos neuronios ate a camada de saida.
            Calculates the values for all neurons until the output layer.

        :param sample: Numpy array containing one data sample.
        :return: Network prediction for this data sample
        """
        temp = sample.copy()
        temp.resize(len(sample), 1)
        np.copyto(self._network[0], temp)

        for i in range(len(self._network) - 1):
            extended = self._network[i].copy()
            # Add bias to input
            bias = np.array([[-1]])
            extended = np.append(extended, bias, axis=0)

            # Calculates the next neuron's output using y(k) = W(k-1) * y(k-1)
            z = self._weights[i].dot(extended)
            self._network[i + 1] = np.apply_along_axis(activate, 1, z)

        # Returns the last layer of the network (which represents the output)
        return self._network[-1]

    def _backprop(self, expected):
        """
        Implements the backpropagation algorithm
        :param expected: Desired value for the actual data sample
        :return: None
        """
        expected = expected.reshape(len(expected), 1)
        error = expected - self._network[-1]
        gradient = np.multiply(error, self.derivative(-1))

        # Update weigths and calculates the new gradient
        for k in range(len(self._network)-2, -1, -1):
            temp = self._back_gradient(gradient, k)
            self.actualize_weights(k, gradient)
            gradient = temp

    def _back_gradient(self, gradient, layer):
        """
            Calculates the gradient of the previous layer based on the values passed to the gradient
        parameter (which must be the gradient for the layer in front, with the backpropagation going
        from output to input)

        :param gradient: Gradient for next layer
        :param layer: Number of layer for which the gradient will be calculated
        :return: Numpy array with gradients for previous layer
        """
        sums = np.zeros(shape=(len(self._network[layer]), 1))
        # TODO make this sum more simple with broadcasting
        for j in range(len(self._network[layer])):
            subsum = 0
            for value, scale in zip(self._weights[layer][:, j], gradient):
                subsum += (scale * value)
            sums[j] = subsum
        return np.multiply(self.derivative(layer), sums)

    def derivative(self, layer):
        """
            Sigmoid function's derivative for use in the backpropagation algorithm.

        :param layer: Number of layer for which the derivative will be calculated
        :return: Numpy array with the derivative values for the neurons
        """
        # self._network is a list of numpy matrices
        return self._network[layer] * (1 - self._network[layer])

    def actualize_weights(self, layer, gradient):
        # This code has no salvation. Burn it in the depths of hell
        extended = self._network[layer].copy()
        bias = np.array([[-1]])
        extended = np.append(extended, bias, axis=0)
        delta = self._step * np.dot(gradient, extended.T)
        result = np.add(self._weights[layer], delta)
        self._weights[layer] = result

    # --- modifiers ---

    def append(self, layer):
        if self.fitted:
            raise AlreadyFittedError("Cannot change network layout after fitting data. Try creating a new mlp network.")
        pass

    def pop(self, layer):
        pass

    def resize(self, layer, size):
        if self.fitted:
            raise AlreadyFittedError("Cannot change network layout after fitting data. Try creating a new mlp network.")
        pass

    def set_step(self, new_step):
        self._step = new_step

    # --- helpers ---

    def describe(self):
        # TODO make this function return a string instead of printing it
        if not self.fitted:
            print("Unfitted MLP network for regression with {0} hidden layers.".format(len(self.neuron_sizes)))
            print("Input and output layers will be deduced from data matrix")
            print("Number of neurons in hidden layer:")
            for size, idx in enumerate(self.neuron_sizes):
                print("layer {0} size: {1}".format(idx, size))
            return

        print("MLP network with {0} layers (counting input and output) with sizes:".format(len(self._network)))
        for idx, layer in enumerate(self._network):
            if idx == 0:
                print("input", end="")
            elif idx == len(self._network)-1:
                print("output", end="")
            else:
                print("hidden", end="")
            print(" layer: {1} neurons".format(idx, len(layer)))

        print("\nMatrix of weights for each neuron. First matrix is for (input -> hidden layer) and so on:")
        for idx, matrix in enumerate(self._weights):
            print("{0}:".format(idx))
            print(matrix)


if __name__ == '__main__':
    """
     This class was implemented for a project from an Artificial Intelligence course. It was forbidden
     to use any framework.
     
     By creating an MLP object with the following constructor:
     
        MLP(4, 3)
    
    You can create a mlp network with 3 layers of 4 neurons each.
    If you pass a list, you can create a custom network with distinct sizes for each layer:
    
        MLP([4, 5, 6, 1])
        
    Equivale a: 4 neurons -> 1st hidden layer
                5 neurons -> 2nd hidden layer
                6 neurons -> 3rd hidden layer
                1 neuron  -> 4th hidden layer
    
    The input and output layers will be defined automatically based on the format
    of the input matrix X and the desired value matrix y.
    """

    import matplotlib.pyplot as plt

    def train_test_split(X_data, y_data, test_size=0.3):
        assert X_data.shape[0] == y_data.shape[0], "X_data must have the same number of data samples as y_data"
        qnt = int(test_size * len(X_data))
        # Chooses the indices for the test class
        index = np.random.choice(range(X_data.shape[0]), size=qnt, replace=False)
        # Mask for training values
        train_mask = np.ones(X_data.shape[0], dtype=bool)
        train_mask[index] = False
        # Separates the arrays into training and test
        X_train, X_test = X_data[train_mask], X_data[~train_mask]
        y_train, y_test = y_data[train_mask], y_data[~train_mask]
        return X_train, X_test, y_train, y_test

    def mse(predict, target):
        # Calculates the error between prediction and desired values
        err = predict - target
        # Calculates the error's norm
        norm = np.linalg.norm(err, axis=1)
        # Calculates the medium squared error
        return np.mean(norm ** 2)

    # Matrix with 2 columns (the weird organization is only for better visualization)
    data = np.array([[0.0, 0.45], [0.0, 0.8], [0.0, 1.4], [0.0, 1.6],
                     [0.1, 0.8],
                     [0.2, 0.7], [0.2, 1.2], [0.2, 1.3], [0.2, 1.5],
                     [0.3, 0.5], [0.3, 1.8],
                     [0.4, 0.2], [0.4, 0.8], [0.4, 1.0], [0.4, 1.2], [0.4, 1.4],
                     [0.5, 0.6], [0.5, 0.7], [0.5, 1.0], [0.5, 1.3], [0.5, 1.9],
                     [0.6, 1.1], [0.6, 1.6],
                     [0.7, 0.2], [0.7, 1.0], [0.7, 1.2],
                     [0.8, 1.0],
                     [0.9, 0.8], [0.9, 1.1], [0.9, 1.6],
                     [1.0, 0.8], [1.0, 1.1]])
    print("Size of data matrix: lines: {0}, columns: {1}".format(*data.shape))

    target = np.array([[0, 0], [0, 1], [0, 1], [1, 1],
                       [0, 1],
                       [0, 1], [0, 1], [0, 1], [1, 1],
                       [0, 0], [1, 1],
                       [0, 0], [0, 1], [0, 1], [0, 1], [1, 1],
                       [0, 0], [0, 1], [0, 1], [1, 1], [1, 1],
                       [0, 1], [1, 1],
                       [0, 0], [0, 1], [1, 1],
                       [0, 1],
                       [0, 0], [1, 1], [1, 1],
                       [0, 0], [1, 1]])
    print("Size of target matrix: lines: {0}, columns: {1}".format(*data.shape))

    data_train, data_test, target_train, target_test = train_test_split(X_data=data, y_data=target, test_size=0.3)

    # Multilayer perceptron with 2 neurons on the internal layer
    clf = MLP(1, 2)

    # This list will keep the error values for each batch
    erros = []
    for _ in range(100):
        alldata = np.concatenate((data_train, target_train), axis=1)
        np.random.shuffle(alldata)
        clf.fit(alldata[:, :-2], alldata[:, -2:])
        predicted = clf.predict(data_test)
        mean_error = mse(predicted, target_test)
        erros.append(mean_error)

    plt.plot(range(len(erros)), erros, color='b')
    plt.xlabel("Iterations")
    plt.ylabel("Medium Squared Error (MSE)")
    plt.show()
