import numpy as np

import library.blocks.continuous


class Motor(library.blocks.continuous.Continuous):
    """Simple second order model of a DC motor (for testing purposes)"""

    _parameters = ('friction', 'dtype')
    _default = dict(dtype=[('phi', '<f8'), ('dphi', '<f8')])

    def f(self, t, x):

        dx = np.zeros(x.shape)
        u = self.u

        dx[0] = x[1]
        dx[1] = u - self.friction*x[1]

        return dx

    def g(self, x):
        return x[0]
