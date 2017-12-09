import numpy as np

import library.discrete


class P(library.discrete.Static):

    dtype = [('u', '<f8')]
    _parameters = ('Kp', 'sample_time')

    def __init__(self, **parameters):

        def g(x, u):
            return self.Kp * u

        super().__init__(g=g, **parameters)


class PID(library.discrete.NormalOrder):

    dtype = [('u', '<f8')]
    _parameters = ('Kp', 'Ki', 'Kd', 'sample_time')

    def __init__(self, **parameters):

        def f(t, x, u):

            Ci, Cd = self._aux_vars

            # Integral: x[0](t) = yi(t)
            x[0] = x[0] + Ci * (u + x[2])
            # Derivative: x[1](t) = yd(t)
            x[1] = - x[1] + Cd * (u - x[2])
            # Previous input
            x[2] = u

            return x

        def g(x, u):

            yp = self.Kp * u
            yi = x[0]
            yd = x[1]

            return yp + yi + yd

        super().__init__(x=np.zeros(3), f=f, g=g, **parameters)

    def _recalculate_aux_vars(self):
        self._aux_vars = (0.5 * self.Ki * self.sample_time,
                          2 * self.Kd / self.sample_time)


class PIDss(library.discrete.ReverseOrder):

    dtype = [('u', '<f8')]
    _parameters = ('Kp', 'Ki', 'Kd', 'sample_time')

    def __init__(self, **parameters):

        def f(t, x, u):

            Ci, Cd = self._aux_vars

            # Integration
            x[0] = x[0] + 2 * Ci * u
            # Derivative
            x[0] = -x[0] + 2 * Cd * u

            return x

        def g(x, u):

            Ci, Cd = self._aux_vars

            yp = self.Kp * u
            yi = x[0] + Ci * u
            yd = x[1] + Cd * u

            return yp + yi + yd

        super().__init__(x=np.zeros(2), f=f, g=g, **parameters)

    def _recalculate_aux_vars(self):
        self._aux_vars = (0.5 * self.Ki * self.sample_time,
                          2 * self.Kd / self.sample_time)
