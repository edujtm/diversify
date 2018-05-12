import unittest
import numpy as np
import splearn as spl


class TestSp(unittest.TestCase):

    def test_constructor(self):
        randomlayers = np.random.randint(1, 6, 5)

        def test_numpy(expected, test):
            for exp, tst in zip(expected, test):
                self.assertTrue(np.array_equal(exp, tst))

        # Teste construtor por valores das camadas
        test_numpy([np.zeros(5) for _ in range(9)], spl.MLP(9, 5)._network)
        # Teste construtor por iteravel
        test_numpy([np.zeros(value) for value in randomlayers], spl.MLP(randomlayers)._network)
        # Teste construtor por inteiro
        test_numpy([np.zeros(9) for _ in range(9)], spl.MLP(9)._network)
        # Teste construtor por pacote
        test_numpy([np.zeros(value) for value in randomlayers], spl.MLP(*randomlayers)._network)

        with self.assertRaises(TypeError):
            wronglayers = np.random.rand(3)
            print("Shape wronglayers: {0}".format(wronglayers.shape))
            # Teste construtor por float
            spl.MLP(3.7)
            # Teste construtor por string
            spl.MLP("marcelinho")
            # Teste construtor por tipo aleatorio
            spl.MLP(int)
            # Teste construtor por array de floats
            spl.MLP(wronglayers)
            # Teste construtor por sequencia de floats
            spl.MLP(*wronglayers)
