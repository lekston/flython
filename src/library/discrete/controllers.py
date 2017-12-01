import numpy as np


class P:

    dtype = [('u', '<f8')]

    def __init__(self, **parameters):

        self.parameters = parameters
        self.x = None
        self.y = np.array([0])

    def __call__(self, t, u):

        self.y = self.parameters['gain'] * u

        return self.y
