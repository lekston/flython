import numpy as np

import library.continuous


class SimpleMotor(library.continuous.Continuous):
    """Simple second order model of a DC motor (for testing purposes)"""

    dtype = [('phi', '<f8'), ('dphi', '<f8')]

    def __init__(self, x, **parameters):

        self._manager = None
        self._solver = None

        def f(t, x):

            dx = np.zeros(x.shape)
            u = self.u

            dx[0] = x[1]
            dx[1] = u - parameters['friction']*x[1]

            return dx

        def g(x):

            return x[0]

        self.f = f
        self.g = g
        self.initial_conditions = x

        self.u = None
        self.x = x
        self.y = self.g(x)


class SimplifiedLongitudinalMotion(library.continuous.Continuous):
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
