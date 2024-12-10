from functools import reduce
from typing import TYPE_CHECKING, Callable, Generator, Optional, TypeAlias

if TYPE_CHECKING:
    from .refinement import RefinementCriterium

# Type alias for a point in the 3D space
Point: TypeAlias = tuple[int, int, Optional[int]]


class Node:
    """
    A class used to represent a node in a Mesh Tree.
    """

    # slots for the Node class
    # to optimize memory usage
    # and prevent dynamic attribute
    __slots__ = (
        "_value",
        "_level",
        "_origin",
        "_parent",
        "_children",
        "_is_tri_dimensional",
        "_absolute_origin",
    )

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
        self._parent: Optional[Node] = parent
        # children nodes stored in a dictionary with the origin as key
        self._children: Optional[dict[Point, Node]] = {}

        # infer if the node is tri-dimensional
        self._is_tri_dimensional: bool = True if self._origin[2] is not None else False

        # compute the absolute origin of the node
        self._absolute_origin: Point = self._compute_absolute_origin()

    def __repr__(self) -> str:
        """
        Method to represent the node as a string.

            Returns:
                str: The string representation of the node.
        """
        return f"Node(value={self._value}, level={self._level}, origin={self._origin}, parent={hash(self._parent)})"

    def is_leaf(self) -> bool:
        """
        Method to evaluate if the node is a leaf.

            Returns:
                bool: True if the node is a leaf, False otherwise.
        """
        return not self._children

    def shall_refine(self, criterium: "RefinementCriterium") -> bool:
        """
        Method to evaluate if the node shall be refined.

            Parameters:
                criterium (RefinementCriterium): The criterium to evaluate the node.

            Returns:
                bool: True if the node shall be refined, False otherwise.
        """
        return criterium.eval(self)

    def neighbor(self, point: Point) -> Optional["Node"]:
        """
        Method to get the neighbor (same level) of the node at a given point.

            Parameters:
                point (Point): The point to evaluate the neighbor.

            Returns:
                Optional[Node]: The neighbor node at the given point.
        """

        if not self._parent:
            return None
        else:
            return self._parent._children.get(point)

    def refine(self, *args, **kwargs) -> None:
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
        # check for a number generator
        with_generator: bool = False
        number_generator: Optional[Callable([[float], None])] = None
        if kwargs.get("number_generator"):
            with_generator = True
            number_generator = kwargs.get("number_generator")

        self._children = {
            origin: Node(
                value=number_generator() if with_generator else self._value,
                level=self._level + 1,
                origin=origin,
                parent=self,
            )
            for origin in origins
        }

        # set current node value
        # to average of children values
        self._value = reduce(
            lambda res, c: res + c.value, self._children.values(), 0.0
        ) / len(self._children)

    def coarsen(self) -> None:
        """
        Method to coarsen the node.

            Parameters:
                None

            Returns:
                None
        """

        # coarsening is only possible if the node has children
        if not self._children:
            return

        # set current node value
        # to average of children values
        self._value = reduce(
            lambda res, c: res + c.value, self._children.values(), 0.0
        ) / len(self._children)

        # remove children
        self._children.clear()

    def inject(self, f: Callable[["Node"], None]) -> None:
        """
        Method to inject a function on the node.

            Parameters:
                f (Callable[[Node], None]): The function to inject.

            Returns:
                None
        """
        # apply function on current node
        f(self)
        # apply function on children nodes
        for child in self._children.values():
            child.inject(f)

    def leafs(self) -> Generator["Node", None, None]:
        """
        Returns a generator of all leaf nodes from current node.

            Returns:
                Generator[Node, None, None]: A generator yielding all leaf nodes.
        """

        def collect_leaves(node: Node) -> Generator[Node, None, None]:
            if not node.children:
                yield node
            else:
                for child in node.children.values():
                    if child:
                        yield from collect_leaves(child)

        return collect_leaves(self)

    @property
    def origin(self) -> Point:
        """
        property for the origin of the node.

            Returns:
                Point: The origin of the node.
        """
        return self._origin

    def _compute_absolute_origin(self) -> Point:
        """
        Method to get the normalized absolute origin of the node.

            Returns:
                Point: The normalized absolute origin of the node.
        """

        level_scale: float = 1 / (2**self._level)

        if self._parent is None:
            return self._origin
        else:
            return (
                self._origin[0] * level_scale + self._parent.absolute_origin[0],
                self._origin[1] * level_scale + self._parent.absolute_origin[1],
                self._origin[2] * level_scale + self._parent.absolute_origin[2]
                if self._is_tri_dimensional
                else None,
            )

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

    @value.setter
    def value(self, value: float) -> None:
        """
        Setter for the value of the node.

            Parameters:
                value (float): The value to set.

            Returns:
                None
        """
        self._value = value

    @property
    def parent(self) -> Optional["Node"]:
        """
        property for the parent of the node.

            Returns:
                Node: The parent of the node.
        """
        return self._parent

    @property
    def children(self) -> Optional[dict[Point, "Node"]]:
        """
        property for the children of the node.

            Returns:
                dict[Point, Node]: The children of the node.
        """
        return self._children

    @property
    def absolute_origin(self) -> Point:
        """
        property for the absolute origin of the node.

            Returns:
                Point: The absolute origin of the node.
        """
        return self._absolute_origin
