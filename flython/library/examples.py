from numpy import zeros

from flython.core import Continuous


class Motor(Continuous):
    """Simple second order model of a DC motor (for testing purposes)"""

    _parameters = ('friction', 'dtype')
    _defaults = dict(friction=1, dtype=[('phi', '<f8'), ('dphi', '<f8')])
    _x = zeros(2)

    def f(self, t, x):

        dx = self._x
        u = self.u

        dx[0] = x[1]
        dx[1] = u - self.friction*x[1]

        return dx

    def g(self, x):
        return x[0]
