import numpy as np

import library.discrete

from core import pslots


class P(library.discrete.Static):

    dtype = [('u', '<f8')]

    def __init__(self, Kp, sample_time=-1):

        self.parameters = pslots(Kp=Kp, sample_time=sample_time)

        def g(x, u):
            return self.parameters.Kp * u

        super().__init__(g=g)


class PID(library.discrete.NormalOrder):

    dtype = [('u', '<f8')]

    def __init__(self, Kp, Ki, Kd, sample_time=-1):

        self.parameters = pslots(
            Kp=Kp, Ki=Ki, Kd=Kd, sample_time=sample_time)

        def f(t, x, u):

            Ci, Cd = self._aux_vars

            # Integration
            x[1] = x[1] + Ci * (u + x[3])
            # Derivative
            x[2] = x[2] + Cd * (u - x[3])
            # Previous input
            x[3] = u

            return x

        def g(x, u):

            yp = self.parameters.Kp * u
            yi = x[1]
            yd = x[2]

            return yp + yi + yd

        super().__init__(x=np.zeros(3), f=f, g=g)

    def _recalculate_aux_vars(self):
        Kp, Ki, Kd, Ts = self.parameters
        self._aux_vars = (0.5 * Ki * Ts, 2 * Kd / Ts)


class PIDss(library.discrete.ReverseOrder):

    dtype = [('u', '<f8')]

    def __init__(self, Kp, Ki, Kd, sample_time=-1):

        self.parameters = pslots(
            Kp=Kp, Ki=Ki, Kd=Kd, sample_time=sample_time)

        def f(t, x, u):

            Ci, Cd = self._aux_vars

            # Integration
            x[0] = x[0] + 2 * Ci * u
            # Derivative
            x[0] = -x[0] + 2 * Cd * u

            return x

        def g(x, u):

            Ci, Cd = self._aux_vars

            yp = self.parameters.Kp * u
            yi = x[0] + Ci * u
            yd = x[1] + Cd * u

            return yp + yi + yd

        super().__init__(x=np.zeros(2), f=f, g=g)

    def _recalculate_aux_vars(self):
        Kp, Ki, Kd, Ts = self.parameters
        self._aux_vars = (0.5 * Ki * Ts, 2 * Kd / Ts)
