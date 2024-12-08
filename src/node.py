from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .refinement import RefinementCriterium

# Type alias for a point in the 3D space
Point: TypeAlias = tuple[int, int, int]


class Node:
    """
    A class used to represent a node in a Tree.
    """

    def __init__(self, value: float, level: int, origin: Point) -> None:
        self._value: float = value
        self._level: int = level
        self._origin: Point = origin

    def shall_refine(self, criterium: "RefinementCriterium") -> bool:
        return criterium.eval(self)

    @property
    def origin(self) -> Point:
        """
        property for the origin of the node.

            Returns:
                Point: The origin of the node.
        """
        return self._origin

    @property
    def level(self) -> int:
        """
        property for the level of the node.

            Returns:
                int: The level of the node.
        """
        return self._level

    @property
    def value(self) -> float:
        """
        property for the value of the node.

            Returns:
                float: The value of the node.
        """
        return self._value
