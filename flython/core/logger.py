import logging

from pathlib import Path

# Create logger
logger = logging.getLogger('FLYTHON LOG')
logger.setLevel(logging.DEBUG)
# handlers instaces
fh = NotImplemented
ch = NotImplemented


def file_logger(level):

    global fh

    # create file handler and set level to debug
    if fh is NotImplemented:
        fh = logging.FileHandler(Path(__file__).parent / 'flython.log')
        fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(fh)
    fh.setLevel(getattr(logging, level.upper()))


def console_logger(level):

    global ch

    # create console handler and set level to warning
    if ch is NotImplemented:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(name)s: %(message)s'))
        logger.addHandler(ch)
    ch.setLevel(getattr(logging, level.upper()))
