import numpy as np

from collections import namedtuple

import library.discrete

# Windvectors
WindvectorXZ = namedtuple('Windvector', ['x', 'Vx', 'Vz'])
WindvectorXY = namedtuple('Windvector', ['x', 'y', 'Vx', 'Vy'])
WindvectorXYZ = namedtuple('Windvector', ['x', 'y', 'z', 'Vx', 'Vy', 'Vz'])
# Waypoints
WaypointXZ = namedtuple('Waypoint', ['x', 'z'])
WaypointXY = namedtuple('Waypoint', ['x', 'y'])
WaypointXYZ = namedtuple('Waypoint', ['x', 'y', 'z'])


class Constant(library.discrete.Static):

    _parameters = ('setpoint', 'sample_time', 'dtype')
    _default = dict(sample_time=-1, dtype=[('r', '<f8')])

    def __init__(self, **parameters):

        def g(x, u):
            return self.setpoint

        super().__init__(g=g, **parameters)


class FlightplanXZ(library.discrete.Static):

    _parameters = ('plan', 'sample_time', 'dtype')
    _default = dict(sample_time=-1, dtype=[('xr', '<f8'), ('zr', '<f8')])

    def __init__(self, **parameters):

        def g(x, u):

            # u contains x_vehicle
            return np.array([u, np.interp(u, self.xinterp, self.zinterp)])

        super().__init__(g=g, **parameters)

        self.xinterp = np.array([waypoint.x for waypoint in self.plan])
        self.zinterp = np.array([waypoint.z for waypoint in self.plan])


class WindfieldXZ(library.discrete.Static):

    _parameters = ('field', 'scale_factor', 'noise_variance',
                   'sample_time', 'dtype')
    _default = dict(scale_factor=1, noise_variance=0, sample_time=-1,
                    dtype=[('Vx', '<f8'), ('Vz', '<f8')])

    def __init__(self, **parameters):

        def g(x, u):

            # u contains x_vehicle
            V = self.scale_factor * np.array([
                np.interp(u, self.xinterp, self.Vxinterp),
                np.interp(u, self.xinterp, self.Vzinterp)
            ])

            return V + self.noise_variance * np.random.randn(2)

        super().__init__(g=g, **parameters)

        self.xinterp = np.array([windvector.x for windvector in self.field])
        self.Vxinterp = np.array([windvector.Vx for windvector in self.field])
        self.Vzinterp = np.array([windvector.Vz for windvector in self.field])
