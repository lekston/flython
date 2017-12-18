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
        # Expand Block
        for obj in reversed(self.__class__.__mro__):
            if '_expand' in obj.__dict__:
                obj._expand(self)
