from .block import Block


class Discrete(Block):

    def _validate(self):
        """Block validation method run by the simulation manager"""

        # When -1 inherit sample time from global settings
        if self.sample_time == -1:
            self.sample_time = self._simulation.sample_time

        if (self.sample_time / self._simulation.sample_time) % 1:
            raise ValueError("Incorrect sample time in block: '{}'\n"
                             "The sample time value should be a multiple"
                             "of the simulation sample time".format(
                                 self.__class__.__name__))

        self._N = round(self.sample_time / self._simulation.sample_time)
        self._prev_step = -self._N


class Static(Discrete):

    def __call__(self, u):

        if self._simulation.current_step - self._prev_step >= self._N:

            self.u = u
            self._prev_step = self._simulation.current_step

        return self.y

    @property
    def y(self):
        return self.g(self.x, self.u)


class NormalOrder(Discrete):

    def __call__(self, u):

        if self._simulation.current_step - self._prev_step >= self._N:

            self.u = u
            self.x = self.f(self.x, u)
            self.y = self.g(self.x, u)
            self._prev_step = self._simulation.current_step

        return self.y


class ReverseOrder(Discrete):

    def __call__(self, u):

        if self._simulation.current_step - self._prev_step >= self._N:

            self.u = u
            self.y = self.g(self.x, u)
            self.x = self.f(self.x, u)
            self._prev_step = self._simulation.current_step

        return self.y
