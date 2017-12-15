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

        self.u = u
        self.x = x
        # f: the state transition function
        self.f = f
        # g: the output function
        self.g = g
        # Last call
        self.last_call = -np.inf

    def __setattr__(self, name, value):

        if name in self._parameters and hasattr(self, '_manager'):
            raise Warning("An attempt to change the parameter"
                          "during simulation detected")

        super().__setattr__(name, value)

    def validate(self, manager):
        """Block validation method invoked by the simulation manager"""
        if (self.sample_time / self._manager.t.step) % 1:
            raise ValueError("Incorrect sample time in: '{}'\n"
                             "The sample time value must be a multiple"
                             "of the simulation sample time".format(
                                 self.__class__.__name__))

        self.sampling_factor = self.sample_time / manager.t.step

        self._manager = manager


class Static(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sampling_time:

            self.u = u
            self.last_call = t

        return self.y

    @property
    def y(self):
        return self.g(self.x, self.u)


class NormalOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sampling_time:

            self.u = u
            self.x = self.f(t, self.x, u)
            self.y = self.g(self.x, u)
            self.last_call = t

        return self.y


class ReverseOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sampling_time:

            self.u = u
            self.y = self.g(self.x, u)
            self.x = self.f(t, self.x, u)
            self.last_call = t

        return self.y
