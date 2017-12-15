class Block:

    __slots__ = ('library', 'parameters')

    def __init__(self, library=None, parameters=None):

        self.library = library
        self.parameters = parameters

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)
