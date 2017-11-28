import numpy as np

import simulation

from core import earray


class Model:
    """Base class for handling mathematical model of a system, represented
    in the state space.

    """
    dtype = NotImplemented

    def __init__(self, f, x):

        self.solver = simulation.parameters.solver(
            f, simulation.parameters.t_beg, x, simulation.parameters.t_end)

    def step(self, t):

        register = earray([])

        while self.solver.t < t:

            self.solver.max_step = t - self.solver.t
            self.solver.step()

            register += earray((self.solver.t, *self.solver.y), self.dtype)

        return register


class SimpleTestModel(Model):
    """Simple first order differential equation (dx = -x + u), for testing
    purposes

    """
    dtype = [('t', '<f8'), ('x', '<f8')]

    def __init__(self, x, obj):

        def f(t, x):
            u = obj.forces_and_moments(t, x)
            return -x + u

        super().__init__(f, x)


class SimplifiedLongitudinalmotion(Model):
    """Simplified model of the longitudinal motion.

    In the scenario under consideration certain simplifications are
    imposed. First, by assuming that a specific control system working
    in the background prevents certain rotational and linear motions,
    it is claimed that velocities v, p, r are all identically equal to
    zero. Additionally, it is assumed that the moment of inertia with
    respect to the y axis is equal one.

    """

    def __init__(self, x, obj):

        def f(t, x):
            """Simplified state-space model of the aircraft longitudinal motion

            Parameters
            ----------
            t : float
                Current time value
            x : array_like, shape (n,)
                Current state vector x(t) such that:
                x[0] is the linear velocity component u(t) in body axes
                x[1] is the linear velocity component w(t) in body axes
                x[2] is the angular velocity component q(t) in body axes
                x[3] is the pitch angle theta(t)
                x[4] is the linear velocity component x(t) in Earth axes
                x[5] is the linear velocity component z(t) in Earth axes

            """
        
            Fx, Fz, M = obj.forces_and_moments()
        
            u, w, q, theta = x[0:4]
        
            # Linear momentum equations
            du = Fx / obj.mass - q * w
            dw = Fz / obj.mass + q * u
            dq = M
        
            dtheta = q
        
            dx = np.cos(theta) * u + np.sin(theta) * w
            dz = -np.sin(theta) * u + np.cos(theta) * w
        
            return np.array([du, dw, dq, dtheta, dx, dz])

        super().__init__(f, x)
