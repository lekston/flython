import numpy as np

from library.rotations import Rbv, Rbs


class Birde:

    # Mass
    mass = 2.3  # kg
    # Geometry
    Sw = 0.455  # m2
    # CL, CD as a function of alpha
    alpha = np.deg2rad(np.arange(-10, 13.5, .5))

    CD = np.array([
        0.03429752, 0.03187472, 0.02963173, 0.02755451,
        0.02563955, 0.02388894, 0.0223033, 0.02088139,
        0.01962508, 0.01853751, 0.01761755, 0.01686654,
        0.01628584, 0.01587513, 0.01563272, 0.01555899,
        0.01565468, 0.0159196, 0.01635397, 0.01695767,
        0.01772838, 0.01866706, 0.01977101, 0.02103213,
        0.02246351, 0.02407981, 0.02589036, 0.02786367,
        0.02999504, 0.0322814, 0.03472952, 0.03734498,
        0.04012049, 0.04305556, 0.04614826, 0.0493968,
        0.05280155, 0.05637242, 0.06009656, 0.06398389,
        0.06802337, 0.07219808, 0.07653291, 0.08121376,
        0.08625241, 0.0915534, 0.09792697
    ])

    CL = np.array([
        -0.4845901, -0.4524575, -0.4202253, -0.3878996,
        -0.3554871, -0.322994, -0.290427, -0.2577926,
        -0.2250974, -0.192348, -0.1595511, -0.1267133,
        -0.09384136, -0.06094195, -0.02802184, 0.004912235,
        0.03785351, 0.07079524, 0.1037306, 0.136653,
        0.1695554, 0.2024313, 0.2352738, 0.2680763,
        0.300832, 0.3335343, 0.3661764, 0.3987518,
        0.4312538, 0.463676, 0.4960117, 0.5282544,
        0.5603979, 0.5924355, 0.6243611, 0.6561683,
        0.6878508, 0.7194026, 0.7508175, 0.7820895,
        0.8132126, 0.844181, 0.8749887, 0.90563,
        0.9360994, 0.9663912, 0.9964998
    ])

    @classmethod
    def external_inputs(cls, x, u):

        g = 9.81
        rho = 1.225

        vel_body = x[0:2]
        theta = x[3]

        # Input vector u consists of thrust T, pitch moment M and wind
        # velocity in vehicle-carried axes system
        T, M, *wind_vel = u

        # Transform wind velocity to body axes system
        wind_vel_body = Rbv(0, theta, 0).dot(wind_vel)

        # Velocity relative to air: aerodynamic velocity.
        vel_aero = vel_body - wind_vel_body[[0, 2]]

        # TAS and q_inf as a functions of aerodynamic velocity
        TAS = np.sqrt(vel_aero.dot(vel_aero))
        q_inf = 0.5 * rho * TAS ** 2

        # Alpha, CL and CD as a functions of aerodynamic velocity
        alpha = np.arctan(vel_aero[1] / vel_aero[0])
        CL = np.interp(alpha, cls.alpha, cls.CL)
        CD = np.interp(alpha, cls.alpha, cls.CD)

        # Lift and drag
        L = q_inf * cls.Sw * CL
        D = q_inf * cls.Sw * CD

        # Transform aerodynamical forces (in stability axes system) to
        # body axes system
        Fa = Rbs(alpha, 0).dot([-D, 0, -L])

        Fg = Rbv(0, theta, 0).dot([0, 0, g * cls.mass])
        # Thrust acts in xb direction
        Fx = Fa[0] + Fg[0] + T
        Fz = Fa[2] + Fg[2]

        return Fx, Fz, M
