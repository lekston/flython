import numpy as np

from collections import namedtuple

from flython import discrete

# Waypoints
WaypointXZ = namedtuple('Waypoint', ['x', 'z'])
WaypointXY = namedtuple('Waypoint', ['x', 'y'])
WaypointXYZ = namedtuple('Waypoint', ['x', 'y', 'z'])


class Constant(discrete.Static):

    _parameters = ('setpoint', 'sample_time', 'dtype')
    _defaults = dict(sample_time=-1, dtype=[('r', '<f8')])

    def g(self, x, u):
        return self.setpoint


class PlannerXZ(discrete.Static):

    _parameters = ('plan', 'sample_time', 'dtype')
    _defaults = dict(sample_time=-1, dtype=[('xr', '<f8'), ('zr', '<f8')])

    def g(self, x, u):

        # u contains x_vehicle
        return np.array([u, np.interp(u, self.xinterp, self.zinterp)])

    def _validate(self):

        self.xinterp = np.array([waypoint.x for waypoint in self.plan])
        self.zinterp = np.array([waypoint.z for waypoint in self.plan])
