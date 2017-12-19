class Block:

    def __init__(self, **parameters):

        self.u = None
        self.x = parameters.pop('x', None)
        self.protect = False

        for name in self._parameters:
            try:
                setattr(self, name, parameters[name])
            except KeyError:
                if name in self._default:
                    setattr(self, name, self._default[name])
                else:
                    raise TypeError("{}() required parameter missing: '{}'".
                                    format(self.__class__.__name__, name))
        # Expand Block
        for obj in reversed(self.__class__.__mro__):
            if '_expand' in obj.__dict__:
                obj._expand(self)

    def __setattr__(self, name, value):

        if name in self._parameters and self.protect:
            raise Warning(
                "Parameter {} in {} changed during simulation".format(
                    self.__class__.__name__, name))
        super().__setattr__(name, value)

    def validate(self, simulation):
        self._simulation = simulation
        for obj in reversed(self.__class__.__mro__):
            if '_validate' in obj.__dict__:
                obj._validate(self)
        self.protect = True


class BlockDef:

    __slots__ = ('library', 'parameters')

    def __init__(self, library=None, parameters=None):

        self.library = library
        self.parameters = parameters

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)


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
