import numpy.lib.recfunctions

import numpy


def concatenate(first, second):

    # If size of first is zero return second
    if not first.size:
        return earray(second)

    try:
        return earray(numpy.append(first, second))
    except TypeError:
        # This exception is for broadcasting controller outputs
        # throughout the whole step size (ZOH interpolation)
        return earray(
            numpy.lib.recfunctions.append_fields(
                first,
                second.dtype.names,
                [numpy.ones(first.size) * el for el in second[0]],
                [val[0] for val in second.dtype.fields.values()]))


class earray(numpy.ndarray):
    """Enhanced version of numpy ndarray. By modifying special methods
    __add__ and __iadd__ it is able to concantenate numpy structured
    arrays. This behaviour differs from standard ndarrays which
    perform adding in a mathematical way.

    """

    def __new__(cls, input_array, dtype=None, parent=None):

        new_array = numpy.asarray(input_array, dtype).view(cls)

        if new_array.shape == ():
            new_array = numpy.asarray([input_array], dtype).view(cls)

        return new_array

    def __array_finalize__(self, obj):

        if obj is None:
            return

    def __array_wrap__(self, out_array, context=None):

        if out_array.shape == ():
            return out_array[()]
        else:
            return numpy.ndarray.__array_wrap__(self, out_array, context)

    def __iadd__(self, other):

        return concatenate(self, other)

    def __add__(self, other):

        return concatenate(self, other)
