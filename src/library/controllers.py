import numpy as np

from scipy.integrate import ode
import block.discrete


class N(block.discrete.Static):

    _parameters = ('Kp', 'sample_time', 'dtype')
    _default = dict(sample_time=-1, dtype=[('u', '<f8')])

    def g(self, x, u):
        return self.Kp * u




# class P(library.discrete.Static):

#     _parameters = ('Kp', 'sample_time', 'dtype')
#     _default = dict(sample_time=-1, dtype=[('u', '<f8')])

#     def __init__(self, **parameters):

#         def g(x, u):
#             return self.Kp * u

#         super().__init__(g=g, **parameters)


# class PID(library.discrete.NormalOrder):

#     _parameters = ('Kp', 'Ki', 'Kd', 'sample_time', 'dtype')
#     _default = dict(sample_time=-1, dtype=[('u', '<f8')])

#     def __init__(self, **parameters):

#         def f(t, x, u):

#             Ci, Cd = self._aux_vars

#             # Integral: x[0](t) = yi(t)
#             x[0] = x[0] + Ci * (u + x[2])
#             # Derivative: x[1](t) = yd(t)
#             x[1] = - x[1] + Cd * (u - x[2])
#             # Previous input
#             x[2] = u

#             return x

#         def g(x, u):

#             yp = self.Kp * u
#             yi = x[0]
#             yd = x[1]

#             return yp + yi + yd

#         super().__init__(x=np.zeros(3), f=f, g=g, **parameters)

#     def _recalculate_aux_vars(self):
#         self._aux_vars = (0.5 * self.Ki * self.sample_time,
#                           2 * self.Kd / self.sample_time)


# class PIrD(library.discrete.NormalOrder):

#     _parameters = ('Kp', 'Ki', 'Kd', 'alpha', 'sample_time', 'dtype')
#     _default = dict(alpha=.1, sample_time=-1, dtype=[('u', '<f8')])

#     def __init__(self, **parameters):

#         def f(t, x, u):

#             Ci, D1, D2 = self._aux_vars

#             # Integral: x[0](t) = yi(t)
#             x[0] = x[0] + Ci * (u + x[2])
#             # Derivative: x[1](t) = yd(t)
#             x[1] = - D1 * x[1] + D2 * (u - x[2])
#             # Previous input
#             x[2] = u

#             return x

#         def g(x, u):

#             yp = self.Kp * u
#             yi = x[0]
#             yd = x[1]

#             return yp + yi + yd

#         super().__init__(x=np.zeros(3), f=f, g=g, **parameters)

#     def _recalculate_aux_vars(self):
#         self._aux_vars = (0.5 * self.Ki * self.sample_time,
#                           (2 * self.alpha - self.sample_time) /
#                           (2 * self.alpha + self.sample_time),
#                           2 * self.Kd / (2 * self.alpha + self.sample_time))


# class PIDRealEuler(library.discrete.NormalOrder):

#     _parameters = ('Kp', 'Ki', 'Kd',  'alpha', 'sample_time', 'dtype')
#     _default = dict(sample_time=-1, dtype=[('u', '<f8')])

#     def __init__(self, **parameters):

#         def f(t, x, u):

#             Ci, Cd = self._aux_vars

#             # Integration
#             x[0] = x[0] + Ci * u

#             # Differentiation
#             yd = Cd * (u - x[2])

#             # Exponential smoothing of the differentiated response
#             x[1] = (1 - self.alpha) * x[1] + self.alpha * yd

#             # Previous input signal
#             x[2] = u

#             return x

#         def g(x, u):

#             yp = self.Kp * u
#             yi = x[0]
#             yd = x[1]

#             return yp + yi + yd

#         super().__init__(x=np.zeros(3), f=f, g=g, **parameters)

#     def _recalculate_aux_vars(self):
#         self._aux_vars = (self.Ki / self.sample_time,
#                           self.Kd / self.sample_time)


# class PIDss(library.discrete.ReverseOrder):

#     _parameters = ('Kp', 'Ki', 'Kd', 'sample_time', 'dtype')
#     _default = dict(sample_time=-1, dtype=[('u', '<f8')])

#     def __init__(self, **parameters):

#         def f(t, x, u):

#             Ci, Cd = self._aux_vars

#             # Integration
#             x[0] = x[0] + 2 * Ci * u
#             # Derivative
#             x[0] = -x[0] + 2 * Cd * u

#             return x

#         def g(x, u):

#             Ci, Cd = self._aux_vars

#             yp = self.Kp * u
#             yi = x[0] + Ci * u
#             yd = x[1] + Cd * u

#             return yp + yi + yd

#         super().__init__(x=np.zeros(2), f=f, g=g, **parameters)

#     def _recalculate_aux_vars(self):
#         self._aux_vars = (0.5 * self.Ki * self.sample_time,
#                           2 * self.Kd / self.sample_time)
