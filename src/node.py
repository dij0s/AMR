from collections import deque
from enum import Enum, auto
from functools import reduce
from typing import TYPE_CHECKING, Callable, Generator, Optional, TypeAlias

if TYPE_CHECKING:
    from .refinement import RefinementCriterium

# Type alias for a point in the 3D space
Point: TypeAlias = tuple[float, float, Optional[float]]


class Direction(Enum):
    """
    Helper class used to represent the direction of a neighbor.
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
        "_absolute_centered_origin",
        "_is_tri_dimensional",
        "gradient",
    )

    def __init__(
        self, value: float, level: int, origin: Point, parent: Optional["Node"] = None
    ) -> None:
        """
        Constructor for the Node class.

            Parameters:
                value (float): The value of the node.
                level (int): The level of the node.
                origin (Point): The origin of the node in its own referential (parent Node).
                parent (Optional[Node]): The parent node of the node. It is None by default.

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
        # compute the absolute centered origin of the node
        self._absolute_centered_origin: Point = self._compute_absolute_centered_origin()

        # gradient of the node
        # only used for debugging
        self.gradient: float = 0.0

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
        neighbors: list[Optional[Node]] = [
            self.neighbor(Direction.RIGHT),
            self.neighbor(Direction.LEFT),
            self.neighbor(Direction.UP),
            self.neighbor(Direction.DOWN),
        ]

        # check if refinement would
        # create an invalid difference
        # as only a one level difference
        # is allowed between neighbors
        next_level: int = self._level + 1
        for neighbor in neighbors:
            if neighbor and abs(neighbor.level - next_level) > 1:
                return False

        return True

    def shall_coarsen(self, criterium: "RefinementCriterium") -> bool:
        """
        Method to evaluate if the node shall be coarsened.

            Parameters:
                criterium (RefinementCriterium): The criterium to evaluate the node.

            Returns:
                bool: True if the node shall be coarsened, False otherwise.
        """

        def finest_neighbor_level(direction: Direction) -> Optional[int]:
            """
            Helper function to get the finest neighbor level in a given direction.
            Traverses the neighbors to find the finest level while considering the
            mirrored direction.

                Parameters:
                    direction (Direction): The direction to evaluate the neighbor.

                Returns:
                    Optional[int]: The finest neighbor level in the given direction.
            """
            neighbor: Optional[Node] = self.neighbor(direction)
            if not neighbor:
                return None

            # if neighbor is leaf
            # return its level
            if neighbor.is_leaf():
                return neighbor.level

            # if neighbor has children
            # return the finest level
            # of its children in mirrored
            # direction (opposite edge)
            match direction:
                case Direction.RIGHT:
                    closest_children: list[Node] = [
                        neighbor.children[(0, 0, None)],
                        neighbor.children[(0, 1, None)],
                    ]
                case Direction.LEFT:
                    closest_children: list[Node] = [
                        neighbor.children[(1, 0, None)],
                        neighbor.children[(1, 1, None)],
                    ]
                case Direction.UP:
                    closest_children: list[Node] = [
                        neighbor.children[(0, 1, None)],
                        neighbor.children[(1, 1, None)],
                    ]
                case Direction.DOWN:
                    closest_children: list[Node] = [
                        neighbor.children[(0, 0, None)],
                        neighbor.children[(1, 0, None)],
                    ]

            # if any of the children
            # is not a leaf, return
            # its level + 1 as it
            # would yield the coarsening
            # conditions to be False
            if not all(child.is_leaf() for child in closest_children):
                return closest_children[0].level + 1

            # all the children
            # in neighbor are
            # of same level
            return closest_children[0].level

        # get neighboring
        # cells levels
        neighbors: map = map(
            finest_neighbor_level,
            [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN],
        )

        for neighbor in neighbors:
            if not neighbor:
                continue
            # check level difference
            # with neighbor's level
            if abs(neighbor - self.level) > 1:
                return False

        return True and not criterium.eval(self)

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
        adjacent_origin: Optional[Point] = None

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

    def chain(self, *direction: Direction) -> Optional["Node"]:
        """
        Method to chain the neighbors of the node in a given direction.

            Parameters:
                direction (Direction): The direction(s) to evaluate the neighbor.

            Returns:
                Optional[Node]: The diagonal neighbor node.
        """
        return reduce(lambda res, d: res.neighbor(d) if res else None, direction, self)

    def buffer(self, n: int) -> list["Node"]:
        """
        Method to buffer the neighbors of the node up to a given distance.

            Parameters:
                n (int): The distance (in number of cells) to buffer the neighbors.

            Returns:
                list[Node]: The buffered neighbors of the node.
        """

        def helper(
            node: "Node",
            nn: int,
            directions: list[Direction],
            neighbors: deque[Optional["Node"]],
        ) -> list[Optional["Node"]]:
            """
            Helper function to recursively buffer the neighbors of the node up to a given distance.

                Parameters:
                    node (Node): The node to evaluate the neighbors.
                    nn (int): The current distance (in number of cells) to buffer the neighbors.
                    directions (list[Direction]): The directions to evaluate the neighbors.
                    neighbors (deque[Optional[Node]]): The buffered neighbors of the node.

                Returns:
                    list[Optional[Node]]: The buffered neighbors of the node.
            """

            # stop recursion
            # if node is None
            if not node:
                return neighbors

            buffered_neighbors: deque[Optional["Node"]] = deque()

            # add itself to the buffer
            buffered_neighbors.append(node)

            # stop recursion if distance
            # to buffer is 0
            if nn == 0:
                return buffered_neighbors + neighbors

            # add neighbors in argument
            # given cardinal directions
            # for the current distance
            for direction in directions:
                for i in range(1, nn + 1):
                    buffered_neighbors.appendleft(node.chain(*[direction] * i))

            # recurse in the diagonal
            # direction
            return helper(
                node.chain(*directions),
                nn - 1,
                directions,
                neighbors + buffered_neighbors,
            )

        cardinal_neighbors: list[Optional[Node]] = []

        # add cardinal neighbors
        # in given distance range
        for direction in [
            Direction.RIGHT,
            Direction.LEFT,
            Direction.UP,
            Direction.DOWN,
        ]:
            for i in range(1, n + 1):
                cardinal_neighbors.append(self.chain(*[direction] * i))

        # filter out None values
        # in cardinal directions
        cardinal_neighbors = [node for node in cardinal_neighbors if node]

        # add square corners
        # recursively and reduce
        # them into a single list
        buffered_neighbors: list[Optional[Node]] = reduce(
            lambda res, directions: helper(
                self.chain(*directions), n - 1, directions, res
            ),
            [
                [Direction.RIGHT, Direction.UP],
                [Direction.LEFT, Direction.UP],
                [Direction.RIGHT, Direction.DOWN],
                [Direction.LEFT, Direction.DOWN],
            ],
            deque(),
        )

        # return the buffered neighbors
        # in cardinal and diagonal directions
        buffered_neighbors.extend(cardinal_neighbors)
        return [node for node in buffered_neighbors if node]

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
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                None
        """

        def interpolate(parent: Node, child_origin: Point) -> float:
            """
            Helper function to interpolate the value of a
            child node using a simple linear interpolation
            between the parent value and the neighbors values.

                Parameters:
                    parent (Node): The current parent node.
                    child_origin (Point): The origin of the child node.

                Returns:
                    float: The interpolated value of the child node.
            """

            # parent value
            value: float = parent.value
            # parent centered
            # coordinates
            x: float = 0.5
            y: float = 0.5

            # get neighbors
            right: Optional[Node] = parent.neighbor(Direction.RIGHT)
            left: Optional[Node] = parent.neighbor(Direction.LEFT)
            up: Optional[Node] = parent.neighbor(Direction.UP)
            down: Optional[Node] = parent.neighbor(Direction.DOWN)

            # compute gradient in the
            # x and y directions
            dx: float = 0.0
            dy: float = 0.0

            # compute gradient using
            # central differences
            if right and left:
                dx = (right.value - left.value) / 2.0
            # fallback to forward
            # differences
            elif right:
                dx = right.value - value
            elif left:
                dx = value - left.value

            # compute gradient using
            # central differences
            if up and down:
                dy = (down.value - up.value) / 2.0
            # fallback to forward
            # differences
            elif up:
                dy = up.value - value
            elif down:
                dy = value - down.value

            # scale gradients
            # to prevent too
            # large jumps
            dx *= 0.1
            dy *= 0.1

            # compute delta x and y
            # destructure child origin
            # and center it
            child_x, child_y, _ = child_origin
            child_x = (child_x * 0.5) + 0.25
            child_y = (child_y * 0.5) + 0.25

            # compute relative position
            # from parent center
            delta_x: float = child_x - x
            delta_y: float = child_y - y

            # compute interpolated value
            child_value: float = value + (delta_x * dx) + (delta_y * dy)

            return child_value

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
        # and for fixed level
        with_generator: bool = False
        number_generator: Optional[Callable([[float], None])] = None

        if kwargs.get("number_generator") is not None:
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
            children_values: list[float] = [
                interpolate(self, origin) for origin in origins
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

    def _compute_absolute_centered_origin(self) -> Point:
        """
        Method to get the normalized absolute centered origin of the node.

            Returns:
                Point: The normalized centered origin of the node.
        """
        level_scale: float = 1 / (2**self._level)

        if self._parent is None:
            return (
                self._origin[0] + 0.5,
                self._origin[1] + 0.5,
                self._origin[2] + 0.5 if self._is_tri_dimensional else None,
            )
        else:
            parent_origin: Point = self._parent.absolute_origin
            return (
                (self._origin[0] + 0.5) * level_scale + parent_origin[0],
                (self._origin[1] + 0.5) * level_scale + parent_origin[1],
                (self._origin[2] + 0.5) * level_scale + parent_origin[2]
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

    @property
    def absolute_centered_origin(self) -> Point:
        """
        property for the absolute centered origin of the node.

            Returns:
                Point: The absolute centered origin of the node.
        """
        return self._absolute_centered_origin
