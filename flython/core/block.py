w1 = "Warning: Parameter '{}.{}' changed during simulation."


class Block:

    def __init__(self, name, simulator, **parameters):

        self._name = name
        self._simulator = simulator
        self.u = None
        self.x = parameters.pop('x', self._x if hasattr(self, '_x') else None)

        # Assign parameters
        for k in self._parameters:
            try:
                setattr(self, k, parameters[k])
            except KeyError:
                if k in self._defaults:
                    setattr(self, k, self._defaults[k])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, k))
        # Per block init
        for sub_block in reversed(self.__class__.__mro__):
            if '_block_init' in sub_block.__dict__:
                sub_block._block_init(self)

    def __setattr__(self, name, value):
        if name in self._parameters and (self._simulator.status is 'running' or
           self._simulator.status is 'stopped'):
            self._simulator._warn(w1.format(self._name, name))
            self.validate()
        super().__setattr__(name, value)

    def validate(self):
        """Perform block validation"""
        for sub_block in reversed(self.__class__.__mro__):
            if '_validate' in sub_block.__dict__:
                sub_block._validate(self)


class Definition:

    __slots__ = ('library', 'parameters')

    def __init__(self, library=None, parameters=None):

        self.library = library
        self.parameters = parameters

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)
