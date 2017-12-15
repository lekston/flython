import numpy as np

import library.continuous


class SimpleMotor(library.continuous.Continuous):
    """Simple second order model of a DC motor (for testing purposes)"""

    _parameters = ('friction', 'dtype')
    _default = dict(dtype=[('phi', '<f8'), ('dphi', '<f8')])

    def __init__(self, x, **parameters):

        def f(t, x):

            dx = np.zeros(x.shape)
            u = self.u

            dx[0] = x[1]
            dx[1] = u - self.friction*x[1]

            return dx

        def g(x):
            return x[0]

        super().__init__(x, f=f, g=g, **parameters)
