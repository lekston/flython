import numpy as np


class Discrete:

    def __init__(self, x=None, u=None, f=lambda t, x, u: x, g=lambda
                 x, u: x, **parameters):

        for name in self._parameters:
            try:
                setattr(self, name, parameters[name])
            except KeyError:
                if name in self._default:
                    setattr(self, name, self._default[name])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, name))

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
        if name in self._parameters:
            try:
                self._recalculate_aux_vars()
            except AttributeError:
                pass


class Static(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sample_time:

            self.u = u
            self.last_call = t

        return self.y

    @property
    def y(self):
        return self.g(self.x, self.u)


class NormalOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sample_time:

            self.u = u
            self.y = self.g(self.x, u)
            self.x = self.f(t, self.x, u)
            self.last_call = t

        return self.y


class ReverseOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sample_time:

            self.u = u
            self.x = self.f(t, self.x, u)
            self.y = self.g(self.x, u)
            self.last_call = t

        return self.y
