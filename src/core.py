import numpy as np
from numpy.lib.recfunctions import append_fields


def concatenate(first, second):

    # If size of first is zero return second
    if not first.size:
        return earray(second)

    try:
        return earray(np.append(first, second))
    except TypeError:
        # This exception is for broadcasting controller outputs
        # throughout the whole step size (ZOH interpolation)
        return earray(
            append_fields(
                first,
                second.dtype.names,
                [np.ones(first.size) * el for el in second[0]],
                [val[0] for val in second.dtype.fields.values()]))


class earray(np.ndarray):
    """Enhanced version of numpy ndarray.

    Rather than performing array addition in a mathematical sense (as
    standard ndarrays do), by overwriting special methods __add__ and
    __iadd__, earray implements concatenation of arguments.

    """

    def __new__(cls, input_array, dtype=None, parent=None):

        new_array = np.asarray(input_array, dtype).view(cls)

        if new_array.shape == ():
            new_array = np.asarray([input_array], dtype).view(cls)

        return new_array

    def __array_finalize__(self, obj):

        if obj is None:
            return

    def __array_wrap__(self, out_array, context=None):

        if out_array.shape == ():
            return out_array[()]
        else:
            return np.ndarray.__array_wrap__(self, out_array, context)

    def __iadd__(self, other):

        return concatenate(self, other)

    def __add__(self, other):

        return concatenate(self, other)
