import pytest
import numpy as np
import numpy.testing as tst
from diversify import splearn as spl


@pytest.fixture()
def xor_data():
    data = np.array([[0, 0],
                     [0, 1],
                     [1, 0],
                     [1, 1]], dtype='float64')
    target = np.array([[0, 0],
                       [1, 0],
                       [1, 0],
                       [0, 1]], dtype='float64')
    return data, target


def test_constructor(xor_data):
    randomlayers = np.random.randint(1, 6, 5)
    data, target = xor_data

    def test_numpy(expected, value):
        expected.insert(0, np.zeros(shape=(2, 1)))
        expected.append(np.zeros(shape=(2, 1)))
        for exp, t in zip(expected, value):
            assert exp.shape == t.shape

    # Test constructor with values for layers
    neural1 = spl.MLP(9, 5).fit(data, target)
    test_numpy([np.zeros(shape=(9, 1)) for _ in range(5)], neural1._network)
    # Test constructor for iterable
    neural2 = spl.MLP(randomlayers).fit(data, target)
    test_numpy([np.zeros(shape=(value, 1)) for value in randomlayers], neural2._network)
    # Test constructor with integer
    neural3 = spl.MLP(9).fit(data, target)
    test_numpy([np.zeros(shape=(9, 1)) for _ in range(9)], neural3._network)
    # Test constructor with package
    neural4 = spl.MLP(*randomlayers).fit(data, target)
    test_numpy([np.zeros(shape=(value, 1)) for value in randomlayers], neural4._network)

    # Testing wrong constructors
    with pytest.raises(TypeError):
        wronglayers = np.random.rand(3)
        print("Shape wronglayers: {0}".format(wronglayers.shape))
        # Test constructor with float
        spl.MLP(3.7)
        # Test constructor with string
        spl.MLP("marcelinho")
        # Test constructor with random type
        spl.MLP(int)
        # Test constructor with array of floats
        spl.MLP(wronglayers)
        # Test constructor with sequence of floats
        spl.MLP(*wronglayers)


def test_fitting(xor_data):
    data, target = xor_data
    ml = spl.MLP([2])
    ml.fit(data, target)

    spl.MLP(2, 1).fit(data, target)


def test_foward():
    weight1 = np.array([[0.3, 0.8, 0.7],
                        [0.5, 0.6, 0.2]])
    weight2 = np.array([[0.1, 0.4, 0.9],
                        [0.5, 0.3, 0.6]])
    first = np.array([[0.0, 0.0]])
    target = np.array([[0.0, 0.0]])
    testinput = np.array([0.0, 0.0])

    neural = spl.MLP(2, 1).fit(first, target)
    neural._weights[0] = weight1
    neural._weights[1] = weight2
    testtarget = np.array([0.33, 0.425]).reshape(2, 1)
    tst.assert_almost_equal(neural._forward(testinput), testtarget, decimal=2)


def test_predict(xor_data):
    data, target = xor_data
    neural = spl.MLP(2, 1).fit(data, target)
    neural.predict(np.array([[1, 1]]))


def test_back():
    weight1 = np.array([[0.3, 0.8, 0.7],
                        [0.5, 0.6, 0.2]])
    weight2 = np.array([[0.1, 0.4, 0.9],
                        [0.5, 0.3, 0.6]])
    first = np.array([[0.0, 0.0]])
    target = np.array([[0.0, 0.0]])
    testinput = np.array([0.0, 0.0])
    expected = np.array([0.0, 0.0])

    # Results from classroom assignment
    nweights = [np.array([[0.3, 0.8, 0.71],
                          [0.5, 0.6, 0.21]]),
                np.array([[0.08, 0.38, 0.93],
                          [0.48, 0.28, 0.65]])]

    neural = spl.MLP(2, 1).fit(first, target)
    neural._weights[0] = weight1
    neural._weights[1] = weight2
    neural._forward(testinput)
    neural._backprop(expected)
    for old, new in zip(neural._weights, nweights):
        tst.assert_almost_equal(old, new, decimal=2)


def test_describe(xor_data):
    data, target = xor_data
    neural = spl.MLP(2, 1).fit(data, target)
    neural.describe()
