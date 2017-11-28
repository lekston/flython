"""Simulation tool and global settings.

The module includes tools and parameters for performing
simulations. Please modify the parameters with caution.

"""
from . import parameters


class _SimulationManager:

    def __init__(self):

        self.t_beg = parameters.t_beg
        self.t_end = parameters.t_end
        self.step_size = parameters.step_size
        self.nsteps = 1

    def __enter__(self):

        return self

    def __iter__(self):

        while self.t < self.t_end:
            yield(self.t)
            self.nsteps += 1

    def __exit__(self, exc_type, exc_value, tb):

        if not exc_type:
            return True

    @property
    def t(self):
        return self.t_beg + self.nsteps * self.step_size


def run(*objects):
    """Run simulation with objects according to the input arguments"""
    with _SimulationManager() as simulation_manager:
        for t in simulation_manager:
            for object_ in objects:
                object_(t)
