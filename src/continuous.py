import numpy as np


class Continuous:

    @property
    def x(self):
        return self.model.solver.y

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Due to the solver requirements the input signals must be
        # passed indirectly using the self._u attribute
        self._u = u

        # Solve equations of motion (up to the time point t) and
        # capture the trajectories
        t, x = self.model.step(t)

        return t, x


class Motor(Continuous):

    dtype = [('phi', '<f8'), ('dphi', '<f8')]

    def __init__(self, model, x):

        # Placeholder for the current value of the system inputs
        self._u = np.array([0])

        # System dynamics model in a state space representation
        self.model = model(x, self)

    def extern(self, t, x):

        return self._u

    @property
    def y(self):
        return self.x[0]
