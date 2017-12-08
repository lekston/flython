import numpy as np


class Discrete:

    def __init__(self, x=None, u=None, f=lambda t, x, u: x, g=lambda x, u: x):

        self._simulation = None

        self.u = u
        self.x = x
        self.last_call = -np.inf

        # f: the state transition function
        self.f = f

        # g: the output function
        self.g = g

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self.parameters:
            self._recalculate_aux_vars()


class Static(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.parameters.sample_time:

            self.u = u
            self.last_call = t

        return self.y

    @property
    def y(self):
        return self.g(self.x, self.u)


class NormalOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.parameters.sample_time:

            self.u = u
            self.y = self.g(self.x, u)
            self.x = self.f(t, self.x, u)
            self.last_call = t

        return self.y


class ReverseOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.parameters.sample_time:

            self.u = u
            self.x = self.f(t, self.x, u)
            self.y = self.g(self.x, u)
            self.last_call = t

        return self.y
