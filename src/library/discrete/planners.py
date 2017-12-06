import numpy as np

from collections import namedtuple

import library.discrete

WaypointXZ = namedtuple('Waypoint', ['x', 'z'])
WaypointXY = namedtuple('Waypoint', ['x', 'y'])
WaypointXYZ = namedtuple('Waypoint', ['x', 'y', 'z'])


class Constant(library.discrete.Discrete):

    dtype = [('r', '<f8')]

    def __init__(self, setpoint, sample_time=-1):

        super().__init__(x=setpoint, sample_time=sample_time)


class FlightplanXZ(library.discrete.Discrete):

    dtype = [('xr', '<f8'), ('zr', '<f8')]

    def __init__(self, plan, sample_time=-1):

        self.xinterp = np.array([waypoint.x for waypoint in plan])
        self.zinterp = np.array([waypoint.z for waypoint in plan])

        def f(t, x):

            x_vehicle = self.u
            return np.array([
                x_vehicle,
                np.interp(x_vehicle, self.xinterp, self.zinterp)
            ])

        super().__init__(f=f, sample_time=sample_time)
