from scipy.integrate import RK45
"""Global simulation parameters.

Attributes of this module are read by other modules during
simulation. Please modify the parameters with caution.

Do not edit the code below the warning comment!

"""

# Default solver settings
solver = RK45
t_beg = 0
t_end = 10
step_size = 0.01

# Verbose switch
verbose = False

# Environment (atmosphere) model settings (to be implemented)

# ****************************************
# * Warning! Do not edit the code below! *
# ****************************************
class Manager:

    def __init__(self, solver):

        self.solver = solver
        self.t_beg = t_beg
        self.t_end = t_end
        self.step_size = step_size
        self.nsteps = 0

    def __enter__(self):

        return self

    def __iter__(self):

        while self.solver.status is not 'finished':
            self.nsteps += 1
            yield(self.t_beg + self.nsteps * self.step_size)

    def __exit__(self, exc_type, exc_value, tb):

        if not exc_type:
            return True
