import numpy as np

import simulation.blocks


class Discrete(simulation.blocks.Block):

    def _expand(self):
        """Expand block by additional attributes"""
        self.last_call = -np.inf

    def __setattr__(self, name, value):

        if name in self._parameters and hasattr(self, '_manager'):
            raise Warning("An attempt to change the parameter"
                          "during simulation detected")

        super().__setattr__(name, value)

    def _validate(self, manager):
        """Block validation method run by the simulation manager"""
        if (self.sample_time / self._manager.t.step) % 1:
            raise ValueError("Incorrect sample time in: '{}'\n"
                             "The sample time value must be a multiple"
                             "of the simulation sample time".format(
                                 self.__class__.__name__))

        self.sampling_factor = self.sample_time / manager.t.step

        self._manager = manager


class Static(Discrete):

    def __call__(self, t, u):

        # n = self.manager.time.n
        
        if t - self.last_call >= self.sample_time:

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
