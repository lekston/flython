import scipy.integrate
import simulation.parameters as parameters


class Solver:
    """The class defines a global default solver used (by all continuous
    objects) during a single simulation.

    """

    def step(self, t):

        if not self.solver:
            solver = getattr(scipy.integrate, parameters.solver)
            self.solver = solver(self.f,
                                 parameters.t_beg,
                                 self.initial_conditions,
                                 parameters.t_end)

        T = []
        X = []

        while self.solver.t < t:

            self.solver.max_step = t - self.solver.t
            self.solver.step()
            T.append(self.solver.t)
            X.append(self.solver.y)

        return T, X
