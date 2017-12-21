import scipy.integrate

from numpy import nextafter

import library.blocks


class Continuous(library.blocks.Block):
    """Base class for continuous models"""

    @property
    def y(self):
        return self.g(self.x)

    def __call__(self, u):
        """Perform a single simulation step, up to the time point t"""

        # Assign input signal
        self.u = u
        # Prepare empty lists for solver results
        T = []
        X = []
        # Run solver (up to the time point t) and store the results
        try:
            t = self._simulation.t
            while self._solver.t < t:
                if nextafter(t, t-1) <= self._solver.t <= nextafter(t, t+1):
                    break
                self._solver.max_step = t - self._solver.t
                self._solver.step()
                T.append((self._solver.t, ))
                X.append(self._solver.y)
            self.x = self._solver.y
        except AttributeError:
            # Create solver instance
            solver = getattr(scipy.integrate, self._simulation.solver)
            self._solver = solver(self.f,
                                  self._simulation.beg,
                                  self.x,
                                  self._simulation.end)
            T, X = self.__call__(u)

        return T, X
