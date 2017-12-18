import numpy as np
import scipy.integrate


class Block:

    def __init__(self, **parameters):

        self.u = None
        self.x = parameters.pop('x', None)

        for name in self._parameters:
            try:
                setattr(self, name, parameters[name])
            except KeyError:
                if name in self._default:
                    setattr(self, name, self._default[name])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, name))


class BlockDefinition:

    __slots__ = ('library', 'parameters')

    def __init__(self, library=None, parameters=None):

        self.library = library
        self.parameters = parameters

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)


class Continuous(Block):
    """Base class for continuous models"""

    def __init__(self, x, u=None, f=lambda t, x, u: x, g=lambda x, u: x,
                 **parameters):

        # Attributes initialized by the simulation manager
        self._manager = None
        self._solver = None

        for name in self._parameters:
            try:
                setattr(self, name, parameters[name])
            except KeyError:
                if name in self._default:
                    setattr(self, name, self._default[name])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, name))

        self.u = u
        self.x = x
        # f: the state transition function
        self.f = f
        # g: the output function
        self.g = g

    @property
    def y(self):
        return self.g(self.x)

    def __call__(self, t, u):
        """Perform a single simulation step, up to the time point t."""

        # Assign input signal
        self.u = u

        T = []
        Y = []
        # Run solver (up to the time point t) and store the results
        if not self._solver:
            solver = getattr(scipy.integrate, self._manager.solver)
            self._solver = solver(self.f,
                                  self._manager.t.beg,
                                  self.x,
                                  self._manager.t.end)

        while self._solver.t < t:
            if np.nextafter(t, t-1) <= self._solver.t <= np.nextafter(t, t+1):
                break
            self._solver.max_step = t - self._solver.t
            self._solver.step()
            T.append((self._solver.t, ))
            Y.append(self._solver.y)

        self.x = self._solver.y

        return T, Y

    def validate(self, manager):
        self._manager = manager


class Discrete(Block):

    def __init__(self, **parameters):
        super().__init__(**parameters)
        self.last_call = -np.inf

    def __setattr__(self, name, value):

        if name in self._parameters and hasattr(self, '_manager'):
            raise Warning("An attempt to change the parameter"
                          "during simulation detected")

        super().__setattr__(name, value)

    def validate(self, manager):
        """Block validation method invoked by the simulation manager"""
        if (self.sample_time / self._manager.t.step) % 1:
            raise ValueError("Incorrect sample time in: '{}'\n"
                             "The sample time value must be a multiple"
                             "of the simulation sample time".format(
                                 self.__class__.__name__))

        self.sampling_factor = self.sample_time / manager.t.step

        self._manager = manager


class Static(Discrete):

    def __call__(self, t, u):

        # n = self.manager.time.n
        
        if t - self.last_call >= self.sample_time:

            self.u = u
            self.last_call = t

        return self.y

    @property
    def y(self):
        return self.g(self.x, self.u)


class NormalOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sampling_time:

            self.u = u
            self.x = self.f(t, self.x, u)
            self.y = self.g(self.x, u)
            self.last_call = t

        return self.y


class ReverseOrder(Discrete):

    def __call__(self, t, u):

        if t - self.last_call >= self.sampling_time:

            self.u = u
            self.y = self.g(self.x, u)
            self.x = self.f(t, self.x, u)
            self.last_call = t

        return self.y


def pslots(**kwargs):

    field_names = tuple(name for name in kwargs.keys())

    def __init__(self, *args, **kwargs):
        attrs = dict(zip(self.__slots__, args))
        attrs.update(kwargs)
        for name, value in attrs.items():
            setattr(self, name, value)

    def __iter__(self):
        return (getattr(self, name) for name in self.__slots__)

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)

    cls_attrs = dict(__slots__=field_names,
                     __init__=__init__,
                     __iter__=__iter__,
                     __repr__=__repr__)

    return type('parameters', (object,), cls_attrs)(**kwargs)
