import numpy as np

import simanager as sm


class Aircraft:

    def __init__(self, model, x, controllers=None):

        self.model = model(x, self)
        # This is a place for defining aircraft specific attributes
        # such as mass, tensor of inertia, aerodynamical coeffs, etc.

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

    def __call__(self):
        """Run simulation"""

        with sm.Manager(self.model.solver) as manager:

            for t_bound in manager:

                self.model.step(t_bound)

                # Here is a place for update control signals by
                # calling the appropriate controllers objects. The
                # list of controllers should be supplied by the
                # simanager.

                # Controllers will be operating according to a given
                # flight plan

                if sm.verbose:
                    print("Solver {}, step {}), t={}, x={}".format(
                        self.model.solver.status, manager.nsteps,
                        self.model.solver.t, self.x))
