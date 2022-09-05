"""Common classes and type aliases within the library."""

from __future__ import annotations

import dataclasses
import enum
import sys
#from collections.abc import Iterable
from typing import final, Optional, TYPE_CHECKING, Union, Tuple, Iterable

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from tetris import BaseGame

if sys.version_info > (3, 10):
    from typing import TypeAlias

    Board: TypeAlias
    Minos: TypeAlias
    Seed: TypeAlias

Board = NDArray[np.int8]
Minos = Iterable[Tuple]
Seed = Union[str, bytes, int]


class PlayingStatus(enum.Enum):
    """Enum representing a game's status.

    Attributes
    ----------
    playing
        The game can proceed normally.
    idle
        The game is temporarily stopped (i.e. it was paused).
    stopped
        The game is permanently stopped (e.g. after a block-out).
    """

    playing = enum.auto()
    idle = enum.auto()
    stopped = enum.auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class MoveKind(enum.Enum):
    """Enum representing a `PartialMove`'s kind of movement.

    Attributes
    ----------
    drag
        Horizontal push.
    hard_drop
        Hard-drop: the piece is pushed to the bottom and locked.
    rotate
        Rotation.
    soft_drop
        Downward push.
    swap
        Swap: the piece is swapped with the hold piece.
    """

    drag = enum.auto()
    hard_drop = enum.auto()
    rotate = enum.auto()
    soft_drop = enum.auto()
    swap = enum.auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class PieceType(enum.IntEnum):
    """Enum representing each piece type.

    Attributes
    ----------
    I
    J
    L
    O
    S
    T
    Z

    See Also
    --------
    MinoType : Suitable for reading board data.
    """

    I = enum.auto()  # noqa
    J = enum.auto()
    L = enum.auto()
    O = enum.auto()  # noqa
    S = enum.auto()
    T = enum.auto()
    Z = enum.auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class MinoType(enum.IntEnum):
    """Enum representing each possible board mino.

    Attributes
    ----------
    EMPTY
    I
    J
    L
    O
    S
    T
    Z
    GHOST
    GARBAGE
    """

    EMPTY = 0
    I = enum.auto()  # noqa
    J = enum.auto()
    L = enum.auto()
    O = enum.auto()  # noqa
    S = enum.auto()
    T = enum.auto()
    Z = enum.auto()
    GHOST = enum.auto()
    GARBAGE = enum.auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclasses.dataclass
class Piece:
    """Object representing a game's piece.

    Usually, this object is only directly instantiated by a
    `tetris.engine.abcs.RotationSystem`.

    Attributes
    ----------
    type : PieceType
        The current piece type this is (e.g. a T piece)
    x : int
        The piece's x coordinate on the board.
    y : int
        The piece's y coordinate on the board.
    r : int
        The piece's rotation, per 90deg clockwise. This is always a number in
        `range(4)`, with 0 being the default (spawn) rotation.
    minos : Minos
        A tuple of (x, y) offsets for this piece's minos (occupied squares). These are
        relative to `x`, `y`.

    Examples
    --------
    >>> import tetris
    >>> game = tetris.BaseGame(seed=128)
    >>> game.piece.r
    0
    >>> game.piece.type
    PieceType.Z
    >>> game.piece.minos
    ((0, 0), (0, 1), (1, 1), (1, 2))
    >>> p = np.zeros((4, 4), dtype=int)
    >>> for x, y in game.piece.minos:
    ...     p[x, y] = 1  # This is enough to correctly draw the piece
    ...
    >>> p
    array([[1, 1, 0, 0],
           [0, 1, 1, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])
    """

    __slots__ = ("type", "x", "y", "r", "minos")

    type: PieceType
    x: int
    y: int
    r: int
    minos: Minos


class PartialMove:
    """Partial version of `MoveDelta` objects.

    This object represents the deltas and the kind of movement fired for a
    specific piece. In general, this class isn't used directly, but rather
    `Move` and `MoveDelta`.

    Attributes
    ----------
    kind : MoveKind
        The kind of movement this represents.
    x : int
        The delta for x.
    y : int
        The delta for y.
    r : int
        The delta for r (rotation).
    auto : bool
        True if this move was performed automatically (e.g. from gravity).

    See Also
    --------
    MoveDelta : The complete form of this class.
    Move : The user version of this class.
    """

    __slots__ = ("kind", "x", "y", "r", "auto")

    def __init__(
        self,
        kind: MoveKind,
        *,
        x: int = 0,
        y: int = 0,
        r: int = 0,
        auto: bool = False,
    ) -> None:
        self.kind = kind
        self.x = x
        self.y = y
        self.r = r % 4
        self.auto = auto

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PartialMove):
            return NotImplemented

        return (
            self.kind == other.kind
            and self.x == other.x
            and self.y == other.y
            and self.r == other.r
        )


@final
class MoveDelta(PartialMove):
    """Object representing a game's registered movement.

    The `x`, `y` and `r` attributes are the absolute deltas -- that is,
    ``piece.x - delta.x`` is equal to the previous state. `rx`, `ry` and `rr`
    are the original values (e.g. the ones provided in a `Move` to
    `tetris.BaseGame.push`).

    Attributes
    ----------
    kind : MoveKind
        The kind of movement this represents.
    x : int
        The delta for x.
    y : int
        The delta for y.
    r : int
        The delta for r (rotation).
    rx : int
        The attempted delta for x.
    ry : int
        The attempted delta for y.
    rr : int
        The attempted delta for r (rotation).
    auto : bool
        True if this move was performed automatically (e.g. from gravity).
    """

    __slots__ = ("game", "rx", "ry", "rr", "clears")

    def __init__(
        self,
        kind: MoveKind,
        *,
        game: BaseGame,
        x: int = 0,
        y: int = 0,
        r: int = 0,
        clears: Optional[list[int]] = None,
        auto: bool = False,
    ) -> None:
        self.kind = kind
        self.game = game
        self.x = x
        self.y = y
        self.r = r % 4
        self.rx = self.x
        self.ry = self.y
        self.rr = self.r
        self.clears = clears or []
        self.auto = auto

    __eq__ = object.__eq__


@final
class Move(PartialMove):
    """Object representing a possible move.

    Attributes
    ----------
    kind : MoveKind
        The kind of movement this represents.
    x : int
        The delta for x.
    y : int
        The delta for y.
    r : int
        The delta for r (rotation).
    auto : bool
        True if this move was performed automatically (e.g. from gravity).
    """

    __slots__ = ()

    @classmethod
    def drag(cls, tiles: int) -> Move:
        """Return a `Move` object representing horizontal movement.

        Parameters
        ----------
        tiles : int
            How many tiles to move. Negative numbers are leftward moves.

        Returns
        -------
        Move
        """
        return cls(MoveKind.drag, y=tiles)

    @classmethod
    def left(cls, tiles: int = 1) -> Move:
        """Return a `Move` object representing leftward movement.

        Parameters
        ----------
        tiles : int, default = 1
            How many tiles to move.

        Returns
        -------
        Move
        """
        return cls(MoveKind.drag, y=-tiles)

    @classmethod
    def right(cls, tiles: int = 1) -> Move:
        """Return a `Move` object representing rightward movement.

        Parameters
        ----------
        tiles : int, default = 1
            How many tiles to move.

        Returns
        -------
        Move
        """
        return cls(MoveKind.drag, y=+tiles)

    @classmethod
    def rotate(cls, turns: int = 1) -> Move:
        """Return a `Move` object representing a piece rotation.

        Parameters
        ----------
        turns : int, default = 1
            How many times to turn clockwise.

        Returns
        -------
        Move
        """
        return cls(MoveKind.rotate, r=turns)

    @classmethod
    def hard_drop(cls) -> Move:
        """Return a `Move` object representing a hard-drop.

        Returns
        -------
        Move
        """
        return cls(MoveKind.hard_drop)

    @classmethod
    def soft_drop(cls, tiles: int = 1) -> Move:
        """Return a `Move` object representing a soft-drop.

        Parameters
        ----------
        tiles : int, default = 1
            How many tiles to move downward.

        Returns
        -------
        Move
        """
        return cls(MoveKind.soft_drop, x=tiles)

    @classmethod
    def swap(cls) -> Move:
        """Return a `Move` object representing a piece swap.

        Returns
        -------
        Move
        """
        return cls(MoveKind.swap)
