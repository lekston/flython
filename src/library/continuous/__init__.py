import scipy.integrate


class Continuous:
    """Solver class for all continuous models"""

    def __init__(self, x=None, u=None):

        self.u = u
        self.x = x

        # Attributes initialized by the simulation manager
        self._manager = None
        self._solver = None

    @property
    def y(self):
        return self.g(self.x)

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Due to the solver requirements the input signals must be
        # passed indirectly using the self.u attribute
        self.u = u

        # Solve equations of motion (up to the time point t) and
        # capture the trajectories
        T, X = self._step(t)
        self.x = X[-1]

        return T, X

    def _step(self, t):

        if not self._solver:
            solver = getattr(scipy.integrate, self._manager.solver)
            self._solver = solver(self.f,
                                  self._manager.t.beg,
                                  self.x,
                                  self._manager.t.end)

        T = []
        X = []

        while self._solver.t < t:

            self._solver.max_step = t - self._solver.t
            self._solver.step()
            T.append(self._solver.t)
            X.append(self._solver.y)

        return T, X
