from enum import Enum, auto
from functools import reduce
from typing import TYPE_CHECKING, Callable, Generator, Optional, TypeAlias

if TYPE_CHECKING:
    from .refinement import RefinementCriterium

# Type alias for a point in the 3D space
Point: TypeAlias = tuple[int, int, Optional[int]]


class Direction(Enum):
    """
    Helper class to represent the direction of a neighbor.
    """

    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


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
        "_absolute_origin",
        "_is_tri_dimensional",
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
        if not criterium.eval(self):
            return False

        # check neighboring cells
        # levels to determine if
        # the node can be refined
        neighbors: list[Node] = [
            self.neighbor(Direction.RIGHT),
            self.neighbor(Direction.LEFT),
            self.neighbor(Direction.UP),
            self.neighbor(Direction.DOWN),
        ]

        # only allow refinement
        # if no neighbor is more
        # than one level coarser
        for neighbor in neighbors:
            if neighbor and neighbor.level + 1 < self.level:
                return False

        # hence, the node can be refined
        # up to one level higher than
        # the coarsest neighbor as
        # the condition herebefore is met
        # as soon as one neighbor is more
        # than one level coarser

        return True

    def shall_coarsen(self) -> bool:
        """
        Method to evaluate if the node shall be coarsened.

            Parameters:
                None

            Returns:
                bool: True if the node shall be coarsened, False otherwise.
        """
        # get neighbors
        neighbors = [
            self.neighbor(Direction.RIGHT),
            self.neighbor(Direction.LEFT),
            self.neighbor(Direction.UP),
            self.neighbor(Direction.DOWN),
        ]

        # only coarsen if no neighbor
        # would end up more than one
        # level different
        for neighbor in neighbors:
            if neighbor and abs(neighbor.level - (self.level - 1)) > 1:
                return False

        return True

    def neighbor(self, direction: Direction) -> Optional["Node"]:
        """
        Method to get the neighbor of the node in a given direction.
        It retrieves the neighbor in given direction of same level or parent node.
        Only supports two-dimensional directions.

            Parameters:
                direction (Direction): The direction to evaluate the neighbor.

            Returns:
                Optional[Node]: The neighbor node in the given direction.
        """
        if not self._parent:
            return None

        # first check if there's a
        # same-level neighbor in
        # parent's children
        x, y, z = self._origin
        adjacent_origin: Point = None

        match direction:
            case Direction.RIGHT:
                adjacent_origin = (x + 1, y, None)
            case Direction.LEFT:
                adjacent_origin = (x - 1, y, None)
            case Direction.UP:
                adjacent_origin = (x, y - 1, None)
            case Direction.DOWN:
                adjacent_origin = (x, y + 1, None)

        # try to find same-level
        # neighbor in current parent
        adjacent_node: Optional[Node] = self._parent._children.get(adjacent_origin)
        if adjacent_node:
            # must check if adjacent
            # node has children
            # only check once as the
            # difference in level is
            # defined to not be greater
            # than one at any given time
            # if not adjacent_node.is_leaf():
            #     child_x: float = x
            #     child_y: float = y
            #     # MAYBE HANDLE DIFFERENTLY
            #     # TO AVOID RETURNING A SINGLE
            #     # CELL BUT MAYBE A WHOLE LINE
            #     match direction:
            #         case Direction.RIGHT:
            #             child_x = 0
            #         case Direction.LEFT:
            #             child_x = 1
            #         case Direction.UP:
            #             child_y = 1
            #         case Direction.DOWN:
            #             child_y = 0

            #     return adjacent_node._children.get((child_x, child_y, None))
            # else:
            return adjacent_node

        # determine which edge of
        # parent cell we're at
        at_parent_edge: bool = False

        match direction:
            case Direction.RIGHT:
                at_parent_edge = x == 1
            case Direction.LEFT:
                at_parent_edge = x == 0
            case Direction.UP:
                at_parent_edge = y == 0
            case Direction.DOWN:
                at_parent_edge = y == 1

        # if we're not at parent's
        # edge, no neighbor exists
        if not at_parent_edge:
            return None

        # get parent's neighbor
        parent_neighbor: Optional[Node] = self._parent.neighbor(direction)
        if not parent_neighbor:
            return None

        # if parent's neighbor has no children,
        # return it (it is one level lower)
        if parent_neighbor.is_leaf():
            return parent_neighbor

        # find the matching child
        # in parent's neighbor
        # need to mirror the coordinates
        # for the opposite edge
        neighbor_x, neighbor_y = x, y
        match direction:
            case Direction.RIGHT:
                neighbor_x = 0
            case Direction.LEFT:
                neighbor_x = 1
            case Direction.UP:
                neighbor_y = 1
            case Direction.DOWN:
                neighbor_y = 0

        neighbor_node: Optional[Node] = parent_neighbor._children.get(
            (neighbor_x, neighbor_y, None)
        )

        # if the neighbor node has
        # children and is at a lower
        # level than current node,
        # traverse down to find the
        # appropriate child
        while (
            neighbor_node
            and neighbor_node.level < self.level
            and not neighbor_node.is_leaf()
        ):
            # compute which child to
            # select based on position
            child_x: float = neighbor_x
            child_y: float = neighbor_y
            match direction:
                case Direction.RIGHT:
                    child_x = 0
                case Direction.LEFT:
                    child_x = 1
                case Direction.UP:
                    child_y = 1
                case Direction.DOWN:
                    child_y = 0

            neighbor_node = neighbor_node._children.get((child_x, child_y, None))

        return neighbor_node

    def adjacent(self, point: Point) -> Optional["Node"]:
        """
        Method to get the adjacent neighbor (same level) of the node at a given point.

            Parameters:
                point (Point): The point to evaluate the neighbor.

            Returns:
                Optional[Node]: The neighbor adjacent node at the given point.
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

        def interpolate(value: float, child_origin: Point) -> float:
            """
            Helper function to interpolate the value of the children nodes.
            It applies a linear interpolation based on the distance from the
            center of the node which holds the value.
            """
            x, y, z = child_origin
            # center node value
            x += 0.5
            y += 0.5
            z = z + 0.5 if z else None

            # get neighboring nodes
            neighbor_values: list = reduce(
                lambda res, node: [*res, node.value] if node else res,
                [
                    self.neighbor(Direction.RIGHT),
                    self.neighbor(Direction.LEFT),
                    self.neighbor(Direction.UP),
                    self.neighbor(Direction.DOWN),
                ],
                [],
            )
            # if we have neighbors,
            # use their average
            neighbor_weight: float = 0.2
            neighbor_influence: float = (
                sum(neighbor_values) / len(neighbor_values) if neighbor_values else 0.0
            )

            # combine current value and
            # neighbor influence
            center_distance: float = (
                (x - 1) ** 2 + (y - 1) ** 2 + (0 if z is None else (z - 1) ** 2)
            ) ** 0.5
            # sqrt(2) or sqrt(3)
            max_distance: float = 1.414 if self._is_tri_dimensional else 2.828
            distance_weight: float = 1 - (center_distance / max_distance)
            interpolated: float = (
                value * (1 - neighbor_weight) * distance_weight
                + neighbor_influence * neighbor_weight
            )

            return interpolated

        # refinement criterium must be
        # applied beforehand and is
        # assumed to be True at this point

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

        if with_generator:
            self._children = {
                origin: Node(
                    value=number_generator(),
                    level=self._level + 1,
                    origin=origin,
                    parent=self,
                )
                for origin in origins
            }
        else:
            # interpolate the value
            # of the children nodes
            # (linearly)
            children_values: list[float] = [
                interpolate(self._value, origin) for origin in origins
            ]

            self._children = {
                origin: Node(
                    value=child_value,
                    level=self._level + 1,
                    origin=origin,
                    parent=self,
                )
                for (origin, child_value) in zip(origins, children_values)
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

        # coarsening is only possible
        # if the node has children
        if not self._children:
            return

        # set current node value
        # to average of children values
        self._value = reduce(
            lambda res, c: res + c.value, self._children.values(), 0.0
        ) / len(self._children)

        # remove children
        self._children.clear()
        self._children = {}

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
            parent_origin: Point = self._parent.absolute_origin
            return (
                self._origin[0] * level_scale + parent_origin[0],
                self._origin[1] * level_scale + parent_origin[1],
                self._origin[2] * level_scale + parent_origin[2]
                if self._is_tri_dimensional
                else None,
            )

    def copy(self) -> "Node":
        """
        Method to copy the node.
        Attention, it is only available to leaf nodes
        as children nodes are not copied !

            Returns:
                Node: A copy of the node.
        """
        if self.children:
            raise ValueError("Only leaf nodes can be copied.")

        return Node(
            value=self._value,
            level=self._level,
            origin=self._origin,
            parent=self._parent,
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
