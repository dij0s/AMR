from functools import reduce
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .refinement import RefinementCriterium

# Type alias for a point in the 3D space
Point: TypeAlias = tuple[int, int, int]


class Node:
    """
    A class used to represent a node in a Mesh Tree.
    """

    def __init__(
        self, value: float, level: int, origin: Point, parent: "Node" = None
    ) -> None:
        """
        Constructor for the Node class.

            Parameters:
                value (float): The value of the node.
                level (int): The level of the node.
                origin (Point): The origin of the node in its own referential (parent Node).
                parent (Node): The parent node of the node. It is None by default.

            Returns:
                None
        """

        self._value: float = value
        self._level: int = level
        self._origin: Point = origin

        # parent node
        self._parent: Node = parent
        # children nodes stored in a dictionary with the origin as key
        self._children: dict[Point, Node] = {}

        # infer if the node is tri-dimensional
        self._is_tri_dimensional: bool = True if self._origin[2] is not None else False

    def __repr__(self) -> str:
        """
        Method to represent the node as a string.

            Returns:
                str: The string representation of the node.
        """
        return f"Node(value={self._value}, level={self._level}, origin={self._origin}, parent={hash(self._parent)})"

    def shall_refine(self, criterium: "RefinementCriterium") -> bool:
        """
        Method to evaluate if the node shall be refined.

            Parameters:
                criterium (RefinementCriterium): The criterium to evaluate the node.

            Returns:
                bool: True if the node shall be refined, False otherwise.
        """
        return criterium.eval(self)

    def is_leaf(self) -> bool:
        """
        Method to evaluate if the node is a leaf.

            Returns:
                bool: True if the node is a leaf, False otherwise.
        """
        return not self._children

    def refine(self) -> None:
        """
        Method to refine the node.

            Parameters:
                None

            Returns:
                None
        """

        # refinement criterium must be
        # applied beforehand and is
        # assumed to be True

        # create children origins
        # for a two or three dimensional node
        origins: list[Point] = (
            [(x, y, z) for x in range(2) for y in range(2) for z in range(2)]
            if self._is_tri_dimensional
            else [(x, y, None) for x in range(2) for y in range(2)]
        )

        # create children nodes
        self._children = {
            origin: Node(
                value=self._value, level=self._level + 1, origin=origin, parent=self
            )
            for origin in origins
        }

        # set current node value
        # to average of children values
        self._value = reduce(
            lambda res, c: res + c.value, self._children.values(), 0.0
        ) / len(self._children)

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

    @property
    def parent(self) -> "Node":
        """
        property for the parent of the node.

            Returns:
                Node: The parent of the node.
        """
        return self._parent

    @property
    def children(self) -> dict[Point, "Node"]:
        """
        property for the children of the node.

            Returns:
                dict[Point, Node]: The children of the node.
        """
        return self._children
