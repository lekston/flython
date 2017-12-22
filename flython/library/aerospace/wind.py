import numpy as np

from collections import namedtuple

from flython.core import discrete

# Windvectors
WindvectorXZ = namedtuple('Windvector', ['x', 'Vx', 'Vz'])
WindvectorXY = namedtuple('Windvector', ['x', 'y', 'Vx', 'Vy'])
WindvectorXYZ = namedtuple('Windvector', ['x', 'y', 'z', 'Vx', 'Vy', 'Vz'])


class WindfieldXZ(discrete.Static):

    _parameters = ('field', 'scale_factor', 'noise_variance',
                   'sample_time', 'dtype')
    _defaults = dict(scale_factor=1, noise_variance=0, sample_time=-1,
                     dtype=[('Vx', '<f8'), ('Vz', '<f8')])

    def g(self, x, u):

        # u contains x_vehicle
        V = self.scale_factor * np.array([
            np.interp(u, self.xinterp, self.Vxinterp),
            np.interp(u, self.xinterp, self.Vzinterp)
        ])

        return V + self.noise_variance * np.random.randn(2)

    def _validate(self):

        self.xinterp = np.array([windvector.x for windvector in self.field])
        self.Vxinterp = np.array([windvector.Vx for windvector in self.field])
        self.Vzinterp = np.array([windvector.Vz for windvector in self.field])
