"""Collection of queue implementations."""

from __future__ import annotations

from tetris.engine import Queue
from tetris.types import PieceType


class SevenBag(Queue):
    """The 7-bag queue randomiser.

    This algorithm is also known as the Random Generator. It was introduced by
    Blue Planet Software and is found in games following the Tetris guideline.

    Notes
    -----
    The algorithm works by creating a "bag" with all the seven tetrominoes and
    shuffling it, then appending it to the queue. Thus, pieces drawn from this
    queue are repeated less often, and it's not possible to have a long run
    without getting a desired piece.
    """

    def fill(self) -> None:  # noqa: D102
        self._pieces.extend(self._random.sample(list(PieceType), 7))


class NES(Queue):
    """The NES queue randomiser.

    This algorithm is used in the original NES Tetris games. It's mostly random
    but has some tweaks to discourage piece repetition.

    Notes
    -----
    This algorithm first rolls an 8-sided die with a face representing each
    tetromino and another face representing a reroll. If the same piece is
    chosen as the one previously drawn or a reroll is chosen, the algorithm
    replaces it with a random piece (possibly a repeat).

    Chances of getting a repeat piece is 1/28 compared to 1/7 for a completely
    random algorithm.
    """

    def fill(self) -> None:  # noqa: D102
        roll = self._random.randint(1, 8)
        try:
            if roll == 8 or PieceType(roll) == self._pieces[-1]:  # last piece in queue
                roll = self._random.randint(1, 7)
            self._pieces.append(PieceType(roll))
        except IndexError:  # queue is empty
            roll = self._random.randint(1, 7)
            self._pieces.append(PieceType(roll))
