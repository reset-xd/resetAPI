"""Basis for core game logic."""

from __future__ import annotations

import abc
import random
import secrets
from typing import Iterable, List
from typing import Iterator
from typing import Sequence
from typing import Optional, overload, TYPE_CHECKING

from tetris.types import Board
from tetris.types import Minos
from tetris.types import MoveDelta
from tetris.types import Piece
from tetris.types import PieceType
from tetris.types import Seed

if TYPE_CHECKING:
    from tetris import BaseGame

__all__ = (
    "Engine",
    "Gravity",
    "Queue",
    "RotationSystem",
    "Scorer",
)


class Engine(abc.ABC):
    """Factory object for parts of game logic.

    Notes
    -----
    All methods receive a `BaseGame` as their arguments, this leaves it up to
    the subclass to initialise those. This is useful, for instance, when
    subclassing one of the engine parts and requiring another part of the game
    to be provided (e.g. providing `game.seed`).
    """

    @abc.abstractmethod
    def gravity(self, game: BaseGame) -> Gravity:
        """Return a new `Gravity` object.

        Returns
        -------
        Gravity
        """
        ...

    @abc.abstractmethod
    def queue(self, game: BaseGame) -> Queue:
        """Return a new `Queue` object.

        Returns
        -------
        Queue
        """
        ...

    @abc.abstractmethod
    def rotation_system(self, game: BaseGame) -> RotationSystem:
        """Return a new `RotationSystem` object.

        Returns
        -------
        RotationSystem
        """
        ...

    @abc.abstractmethod
    def scorer(self, game: BaseGame) -> Scorer:
        """Return a new `Scorer` object.

        Returns
        -------
        Scorer
        """
        ...


class Gravity(abc.ABC):
    """Abstract base class for gravity implementations.

    Parameters
    ----------
    game : BaseGame
        The game this should operate on.
    """

    def __init__(self, game: BaseGame):
        self.game = game

    @classmethod
    def from_game(cls, game: BaseGame) -> Gravity:
        """Construct this object from a game object."""
        return cls(game=game)

    @abc.abstractmethod
    def calculate(self, delta: Optional[MoveDelta] = None) -> None:
        """Calculate the piece's drop and apply moves.

        This function is called on every `tetris.BaseGame.tick` and
        `tetris.BaseGame.push`. It should take care of timing by itself.

        Parameters
        ----------
        delta : MoveDelta, optional
            The delta, if called from `tetris.BaseGame.push`. This is also not
            provided if the last move was automatic, to prevent recursion.
        """
        ...


class Queue(abc.ABC, Sequence):
    """Abstract base class for queue implementations.

    This class extends `collections.abc.Sequence` and consists of `PieceType`
    values. The length is always 7.

    Notes
    -----
    This class provides a `pop` method to remove and return the *first* piece
    in the queue.

    For subclassing, you are expected to use the `_random` attribute (a
    `random.Random` object) and update `_pieces` (a list of `tetris.PieceType`
    which should have a length of *at least* 7). Usually, the only method that
    needs to be overrided is `fill`.

    Examples
    --------
    Since most boilerplate is taken care of under the hood, it's really simple
    to subclass this and implement your own queue randomiser. The source code
    for the `SevenBag` class is itself a good example::

        class SevenBag(Queue):
            def fill(self) -> None:
                self._pieces.extend(self._random.sample(list(PieceType), 7))
    """

    def __init__(
        self,
        pieces: Optional[Iterable[int]] = None,
        seed: Optional[Seed] = None,
        refill: int = 7,
    ):
        seed = seed or secrets.token_bytes()
        self._seed = seed
        self._random = random.Random(seed)
        self._pieces = [PieceType(i) for i in pieces or []]
        self._refill = refill
        while len(self._pieces) <= self._refill:
            # while instead of if for queue methods that call one piece at a time
            self.fill()

    @classmethod
    def from_game(cls, game: BaseGame) -> Queue:
        """Construct this object from a game object."""
        return cls(seed=game.seed)

    def pop(self) -> PieceType:
        """Remove and return the first piece of the queue."""
        while len(self._pieces) <= self._refill:
            self.fill()

        return self._pieces.pop(0)

    @abc.abstractmethod
    def fill(self) -> None:
        """Refill the queue's pieces.

        Notes
        -----
        Internally, this is called automatically when the queue is exhausted.
        """
        ...

    @property
    def seed(self) -> Seed:
        """The random seed being used."""
        return self._seed

    def __iter__(self) -> Iterator[PieceType]:
        for i, j in enumerate(self._pieces):
            if i >= 7:
                break
            yield j

    @overload
    def __getitem__(self, i: int) -> PieceType:
        ...

    @overload
    def __getitem__(self, i: slice) -> List[PieceType]:
        ...

    def __getitem__(self, i):
        return self._pieces[:7][i]

    def __len__(self) -> int:
        return 7

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} object "
            f"[{', '.join(i.name for i in self) + ', ...'}]>"
        )


class RotationSystem(abc.ABC):
    """Abstract base class for rotation systems.

    Parameters
    ----------
    board : tetris.types.Board
        The board this should operate on.
    """

    def __init__(self, board: Board):
        self.board = board

    @classmethod
    def from_game(cls, game: BaseGame) -> RotationSystem:
        """Construct this object from a game object."""
        return cls(board=game.board)

    @abc.abstractmethod
    def spawn(self, piece: PieceType) -> Piece:
        """Return a new piece with a given type.

        Parameters
        ----------
        piece : PieceType
            The piece type to use.

        Returns
        -------
        Piece
            The generated `tetris.Piece` object.
        """
        ...

    @abc.abstractmethod
    def rotate(self, piece: Piece, r: int) -> None:
        """Rotate the given piece in-place.

        Parameters
        ----------
        piece : Piece
            The piece object.
        r : int
            The `r` (rotation) offset.
        """
        ...

    @overload
    def overlaps(self, piece: Piece) -> bool:
        ...

    @overload
    def overlaps(self, minos: Minos, px: int, py: int) -> bool:
        ...

    def overlaps(self, piece=None, minos=None, px=None, py=None):
        """Check if a piece's minos would overlap with anything.

        This method expects either `piece`, or `minos`, `px` and `py` to be
        provided.

        Parameters
        ----------
        piece : tetris.Piece, optional
            The piece object to check against.
        minos : tetris.types.Minos, optional
            The piece's minos to check.
        px : int, optional
            The piece x position.
        py : int, optional
            The piece y position.

        Raises
        ------
        TypeError
            The incorrect arguments were provided.
        """
        if piece is not None:
            minos = piece.minos
            px = piece.x
            py = piece.y

        for x, y in minos:
            if x + px not in range(self.board.shape[0]):
                return True

            if y + py not in range(self.board.shape[1]):
                return True

            if self.board[x + px, y + py] != 0:
                return True

        return False


class Scorer(abc.ABC):
    """Abstract base class for score systems.

    Attributes
    ----------
    score : int
        The current game score
    level : int
        The current game level
    """

    score: int
    start_level: int  # starting level can affect diffrent scoring systems
    level: int
    line_clears: int

    def __init__(self) -> None:
        self.score = 0
        self.start_level = 1
        self.level = 1
        self.line_clears = 0

    @classmethod
    def from_game(cls, game: BaseGame) -> Scorer:
        """Construct this object from a game object."""
        return cls()

    @abc.abstractmethod
    def judge(self, delta: MoveDelta) -> None:
        """Judge a game's move.

        Parameters
        ----------
        delta : tetris.MoveDelta
        """
        ...
