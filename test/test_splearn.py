import unittest
import numpy as np
import splearn as spl
import sklearn as skl

class TestSp(unittest.TestCase):

    def setUp(self):
        self.data = np.array([[0, 0],
                              [0, 1],
                              [1, 0],
                              [1, 1]])
        self.target = np.array([[0, 0],
                                [1, 0],
                                [1, 0],
                                [0, 1]])

    first = np.array([0, 0])
    weight1 = np.array([[0.3, 0.8, 0.7],
                        [0.5, 0.6, 0.2]])
    weight2 = np.array([])

    def test_fitting(self):

        ml = spl.MLP([2])
        ml.fit(self.data, self.target)
        for layer in ml._network:
            print(layer)

    def test_predict(self):
        pass

    def test_back(self):
        pass