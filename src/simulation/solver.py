import scipy.integrate
import simulation.parameters as parameters


class Solver:
    """Default simulation solver class"""

    def __init__(self, f, x):

        solver = getattr(scipy.integrate, parameters.solver)
        self.solver = solver(f, parameters.t_beg, x, parameters.t_end)

    def step(self, t):

        tarr = []
        xarr = []

        while self.solver.t < t:

            self.solver.max_step = t - self.solver.t
            self.solver.step()
            tarr.append(self.solver.t)
            xarr.append(self.solver.y)

        return tarr, xarr
