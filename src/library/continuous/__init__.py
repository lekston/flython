import scipy.integrate
import simulation.parameters as parameters


class Continuous:
    """Solver class for all continuous models"""

    def _step(self, t):

        if not self._solver:
            solver = getattr(scipy.integrate, parameters.solver)
            self._solver = solver(self.f,
                                  parameters.t_beg,
                                  self.initial_conditions,
                                  parameters.t_end)

        T = []
        X = []

        while self._solver.t < t:

            self._solver.max_step = t - self._solver.t
            self._solver.step()
            T.append(self._solver.t)
            X.append(self._solver.y)

        return T, X

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Due to the solver requirements the input signals must be
        # passed indirectly using the self.u attribute
        self.u = u

        # Solve equations of motion (up to the time point t) and
        # capture the trajectories
        T, X = self._step(t)
        self.x = X[-1]
        self.y = self.g(self.x)

        return T, X
