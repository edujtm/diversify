import unittest
import numpy as np
import numpy.testing as tst
from diversify import splearn as spl


class TestSp(unittest.TestCase):

    def setUp(self):
        self.data = np.array([[0, 0],
                              [0, 1],
                              [1, 0],
                              [1, 1]], dtype='float64')
        self.target = np.array([[0, 0],
                                [1, 0],
                                [1, 0],
                                [0, 1]], dtype='float64')

    def test_constructor(self):
        randomlayers = np.random.randint(1, 6, 5)

        def test_numpy(expected, value):
            expected.insert(0, np.zeros(shape=(2, 1)))
            expected.append(np.zeros(shape=(2, 1)))
            for exp, t in zip(expected, value):
                self.assertTrue(exp.shape, t.shape)

        # Test constructor with values for layers
        neural1 = spl.MLP(9, 5).fit(self.data, self.target)
        test_numpy([np.zeros(shape=(9, 1)) for _ in range(5)], neural1._network)
        # Test constructor for iterable
        neural2 = spl.MLP(randomlayers).fit(self.data, self.target)
        test_numpy([np.zeros(shape=(value, 1)) for value in randomlayers], neural2._network)
        # Test constructor with integer
        neural3 = spl.MLP(9).fit(self.data, self.target)
        test_numpy([np.zeros(shape=(9, 1)) for _ in range(9)], neural3._network)
        # Test constructor with package
        neural4 = spl.MLP(*randomlayers).fit(self.data, self.target)
        test_numpy([np.zeros(shape=(value, 1)) for value in randomlayers], neural4._network)

        # Testing wrong constructors
        with self.assertRaises(TypeError):
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

    def test_fitting(self):
        ml = spl.MLP([2])
        ml.fit(self.data, self.target)
        for layer in ml._network:
           print(layer)

        spl.MLP(2, 1).fit(self.data, self.target)

    def test_foward(self):
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

    def test_predict(self):
        neural = spl.MLP(2, 1).fit(self.data, self.target)
        result = neural.predict(np.array([[1, 1]]))
        print("prediction:", result)

    def test_back(self):
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

    def test_describe(self):
        neural = spl.MLP(2, 1).fit(self.data, self.target)
        neural.describe()

    def test_batch(self):
        pass

    def test_iris(self):
        pass