import library.blocks.discrete


class Constant(library.blocks.discrete.Static):

    _parameters = ('setpoint', 'sample_time', 'dtype')
    _default = dict(sample_time=-1, dtype=[('r', '<f8')])

    def g(self, x, u):
        return self.setpoint
