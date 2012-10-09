# -*- coding: utf-8 -*-
"""
    ranking
    ~~~~~~~

    :class:`Ranking` and various strategies for assigning rankings.

    :copyright: (c) 2012 by Heungsub Lee
    :license: BSD, see LICENSE for more details.
"""
import itertools


__copyright__ = 'Copyright 2012 by Heungsub Lee'
__version__ = '0.1.2'
__license__ = 'BSD'
__author__ = 'Heungsub Lee'
__author_email__ = 'h''@''subl.ee'
__url__ = 'http://packages.python.org/ranking'
__all__ = ['Ranking', 'COMPETITION', 'MODIFIED_COMPETITION', 'DENSE',
           'ORDINAL', 'FRACTIONAL']


def COMPETITION(start, length):
    """Standard competition ranking ("1224" ranking)"""
    for x in xrange(length):
        yield start
    yield start + length


def MODIFIED_COMPETITION(start, length):
    """Modified competition ranking ("1334" ranking)"""
    for x in xrange(length):
        yield start + length - 1
    yield start + length


def DENSE(start, length):
    """Dense ranking ("1223" ranking)"""
    for x in xrange(length):
        yield start
    yield start + 1


def ORDINAL(start, length):
    """Ordinal ranking ("1234" ranking)"""
    return xrange(start, start + length + 1)


def FRACTIONAL(start, length):
    """Fractional ranking ("1 2.5 2.5 4" ranking)"""
    avg = (2 * start + length - 1) / float(length)
    for x in xrange(length):
        yield avg
    yield start + length


class Ranking(object):
    """:class:`Ranking` looks like :func:`enumerate` but generates a `tuple`
    containing a rank instead of an index and the values obtained from
    iterating over `sequence`:

    >>> scores = [10, 8, 7, 4]
    >>> list(Ranking(scores))
    [(0, 10), (1, 8), (2, 7), (3, 4)]

    In most cases, rank is equivalent to index. But which values would share
    same score. Then it follows a way that the strategy for assigning ranking
    describes. A strategy is a function that parameterized by `start`, `length`
    and assigns ranks to the tie scores and the next:

    >>> scores = [10, 8, 8, 6]
    >>> list(Ranking(scores)) # strategy defaults to COMPETITION
    [(0, 10), (1, 8), (1, 8), (3, 6)]
    >>> list(Ranking(scores, DENSE))
    [(0, 10), (1, 8), (1, 8), (2, 6)]
    >>> list(Ranking(scores, FRACTIONAL))
    [(0, 10), (1.5, 8), (1.5, 8), (3, 6)]
    >>> list(FRACTIONAL(1, 2))
    [1.5, 1.5, 3]

    :param sequence: sorted score sequence
    :param strategy: a strategy for assigning rankings. Defaults to
                     :func:`COMPETITION`.
    :param start: a first rank. Defaults to 0.
    :param cmp: a comparation function. Defaults to :func:`cmp`.
    :param key: a function to get score from a value
    """

    def __init__(self, sequence=None, strategy=COMPETITION, start=0, cmp=cmp,
                 key=None):
        if sequence is None:
            self.sequence = []
        else:
            self.sequence = sequence
        self.strategy = strategy
        self.start = start
        self.cmp = cmp
        self.key = key

    def __iter__(self):
        rank, drawn, tie_started, final = self.start, [], None, object()
        iterator = iter(self.sequence)
        right = iterator.next()
        right_score = right if self.key is None else self.key(right)
        for value in itertools.chain(iterator, [final]):
            left, right = right, value
            left_score = right_score
            if value is not final:
                right_score = right if self.key is None else self.key(right)
            if left_score is None:
                yield None, left
                continue
            elif value is final:
                compared = 1
            else:
                compared = self.cmp(left_score, right_score)
            if compared < 0: # left is less than right
                raise ValueError('Not sorted by score')
            elif compared == 0: # same scores
                if tie_started is None:
                    tie_started = rank
                drawn.append(left)
                continue
            elif drawn:
                drawn.append(left)
                for rank in self.strategy(tie_started, len(drawn)):
                    try:
                        yield rank, drawn.pop(0)
                    except IndexError:
                        pass
                tie_started = None
                continue
            yield rank, left
            rank += 1

    def iterranks(self):
        for rank, value in self:
            yield rank

    def ranks(self):
        return list(self.iterranks())

    def itervalues(self):
        for rank, value in self:
            yield value

    def values(self):
        return list(self.itervalues())
