import numpy as np

from core import earray


class Aircraft:

    def __init__(self, model, x, controllers=None):

        # EOM model
        self.model = model(x, self)

        # Controllers
        if controllers is None:
            self.controllers = []

    @property
    def x(self):
        return self.model.solver.y

    def forces_and_moments(self, t, x):

        # Here the state of the environment (atmosphere) as well as
        # control inputs should be read. The atmosphere will be
        # available through the simanager.

        # The method is also able to read aircraft specific attributes
        # (using self), therefore this is a place where all
        # informations required by model to proceed a single numerical
        # step are availbe.

        return np.array([1.0])

    def __call__(self, t):
        """Perform a single simulation step, up to the time point t."""

        # Solve objects equations of motion (up to the time point t)
        # and capture the trace data
        state_and_signals = self.model.step(t)

        # Update controllers' signals
        for controller in self.controllers:

            state_and_signals += earray(
                (t, *controller.output), controller.dtype)

            controller.update(self)

        return state_and_signals
