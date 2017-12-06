import numpy as np


class Discrete:

    def __init__(self, x=None, u=None, f=lambda t, x: x, g=lambda x:
                 x, sample_time=-1):

        self._simulation = None

        self.u = u
        self.x = x
        self.last_call = -np.inf
        self.sample_time = sample_time

        # f: the state transition function
        self.f = f

        # g: the output function
        self.g = g

    @property
    def y(self):
        return self.g(self.x)

    def __call__(self, t, u):

        if t - self.last_call >= self.sample_time:

            self.u = u
            self.x = self.f(t, self.x)
            self.last_call = t

        return self.y
