def parameters(field_names):

    try:
        field_names = field_names.replace(',', ' ').split()
    except AttributeError:  # no .replace or .split
        # assume it's already a sequence of identifiers field_names =
        # tuple(field_names)
        pass

    def __init__(self, *args, **kwargs):
        attrs = dict(zip(self.__slots__, args))
        attrs.update(kwargs)
        for name, value in attrs.items():
            setattr(self, name, value)

    def __iter__(self):
        return (name for name in self.__slots__)

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(n, getattr(self, n)) for n
                           in self.__slots__)
        return '{}({})'.format(self.__class__.__name__, values)

    cls_attrs = dict(__slots__=field_names,
                     __init__=__init__,
                     __iter__=__iter__,
                     __repr__=__repr__)

    return type('parameters', (object,), cls_attrs)
