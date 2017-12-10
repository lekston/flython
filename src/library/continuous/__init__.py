import scipy.integrate

import numpy as np


class Continuous:
    """Base class for continuous models"""

    def __init__(self, x, u=None, f=lambda t, x, u: x, g=lambda x, u: x,
                 **parameters):

        # Attributes initialized by the simulation manager
        self._manager = None
        self._solver = None

        for name in self._parameters:
            try:
                setattr(self, name, parameters[name])
            except KeyError:
                if name in self._default:
                    setattr(self, name, self._default[name])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, name))

        self.u = u
        self.x = x
        # f: the state transition function
        self.f = f
        # g: the output function
        self.g = g

    @property
    def y(self):
        return self.g(self.x)

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Assign input signal
        self.u = u

        T = []
        X = []
        # Run solver (up to the time point t) and store the results
        if not self._solver:
            solver = getattr(scipy.integrate, self._manager.solver)
            self._solver = solver(self.f,
                                  self._manager.t.beg,
                                  self.x,
                                  self._manager.t.end)

        while self._solver.t < t:
            if np.nextafter(t, t-1) <= self._solver.t <= np.nextafter(t, t+1):
                break
            self._solver.max_step = t - self._solver.t
            self._solver.step()
            T.append(self._solver.t)
            X.append(self._solver.y)

        self.x = self._solver.y

        return T, X
