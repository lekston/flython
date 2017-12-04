import library.discrete


class Constant(library.discrete.Discrete):

    dtype = [('r', '<f8')]

    def __init__(self, setpoint, sample_time):

        def f(t, x):
            return x

        def g(x):
            return x

        self.f = f
        self.g = g

        super().__init__(x=setpoint, sample_time=sample_time)
