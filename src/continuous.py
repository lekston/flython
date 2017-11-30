import numpy as np


class Continuous:

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Due to the solver requirements the input signals must be
        # passed indirectly using the self.u attribute
        self.u = u

        # Solve equations of motion (up to the time point t) and
        # capture the trajectories
        T, X = self.model.step(t)
        self.x = X[-1]
        self.y = self.model.g(self.x)

        return T, X


class Motor(Continuous):

    dtype = [('phi', '<f8'), ('dphi', '<f8')]

    def __init__(self, model, x):

        # System dynamics model in a state space representation
        self.model = model(x, self)
        self.u = None
        self.x = x
        self.y = self.model.g(x)

    def force(self, t, x):

        return self.u
