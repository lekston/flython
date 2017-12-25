import scipy.integrate

from .block import Block

w1 = "Warning: Solver failed, t={:g}, max_step={:g}."


class Continuous(Block):
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
            t = self._simulator.t
            while self._solver.t < t:
                self._solver.max_step = t - self._solver.t
                self._solver.step()
                T.append((self._solver.t, ))
                X.append(self._solver.y)
            self.x = self._solver.y
        except AttributeError:
            # Create solver instance
            solver = getattr(scipy.integrate, self._simulator.solver)
            self._solver = solver(self.f,
                                  self._simulator.t_beg,
                                  self.x,
                                  self._simulator.t_end)
            T, X = self.__call__(u)
        except RuntimeError:
            self._solver.status = 'running'
            self._simulator.warn(
                w1.format(self._solver.t, self._solver.max_step))

        return T, X
