from flython.blockset import discrete


class Constant(discrete.Static):

    _parameters = ('setpoint', 'sample_time', 'dtype')
    _defaults = dict(sample_time=-1, dtype=[('r', '<f8')])

    def g(self, x, u):
        return self.setpoint
