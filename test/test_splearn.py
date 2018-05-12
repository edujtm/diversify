import unittest
import numpy as np
import splearn as spl

class TestSp(unittest.TestCase):


    def test_constructor(self):
        randomlayers = np.random.randint(1, 6, 5)
        # Teste construtor por valores das camadas
        self.assertEqual([[0.0] * 5 for _ in range(9)], spl.MLP(9, 5).network)
        # Teste construtor por iteravel
        self.assertEqual([[0.0] * value for value in randomlayers], spl.MLP(randomlayers).network)
        # Teste construtor por inteiro
        self.assertEqual([[0.0] * 9 for _ in range(9)], spl.MLP(9).network)
        # Teste construtor por pacote
        self.assertEqual([[0.0] * value for value in randomlayers], spl.MLP(*randomlayers).network)

        with self.assertRaises(TypeError):
            wronglayers = np.random.rand(3)
            print("Shape wronglayers: {0}".format(wronglayers.shape))
            # Teste construtor por float
            neural = spl.MLP(3.7)
            # Teste construtor por string
            neural = spl.MLP("marcelinho")
            # Teste construtor por tipo aleatorio
            neural = spl.MLP(int)
            # Teste construtor por array de floats
            neural = spl.MLP(wronglayers)
            # Teste construtor por sequencia de floats
            neural = spl.MLP(*wronglayers)