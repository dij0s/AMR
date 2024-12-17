from abc import ABC, abstractmethod
from functools import reduce
from math import log
from typing import TYPE_CHECKING, Callable, Optional

from .node import Direction

if TYPE_CHECKING:
    from .node import Node


class RefinementCriterium(ABC):
    """
    This class is used to define a refinement criterium.
    """

    @abstractmethod
    def eval(self, node: "Node") -> bool:
        """
        Evaluates the refinement criterium for a given Node.
        """
        pass

    @staticmethod
    def handle_neighbor(
        current_node: "Node", node: "Node", direction: Direction
    ) -> tuple[Optional[float], float]:
        """
        Helper function to handle a neighbor node.
        It looks for children in given direction.

            Parameters:
                current_node (Node): The current node.
                node (Node): The node to handle (hence neighbor).
                direction (Direction): The direction to look for children.

            Returns:
                tuple[Optional[float], float]: The neighbor node's value and the factor used for the gradient computation.
        """

        if node is None:
            return (None, 0.0)

        # if neighbor is leaf
        # and coarser, must
        # copmute the distance
        # to the current node
        if node.is_leaf() and node.level < current_node.level:
            # for a finer current node
            # the distance to a coarser
            # neighbor is sqrt(0.25²+0.75²)
            return (node.value, 0.7905)

        # if neighbor is leaf
        # at same level
        if node.is_leaf():
            return (node.value, 1.0)

        # if neighbor is not leaf
        # hence has children
        # then current node is coarser
        # and looking at finer nodes
        _, _, z = node.origin
        # get children's value in
        # mirrored direction
        match direction:
            case Direction.RIGHT:
                # interpolate value
                # from leftmost children
                value: float = (
                    node.children[(0, 0, z)].value + node.children[(0, 1, z)].value
                ) / 2
            case Direction.LEFT:
                # interpolate value
                # from rightmost children
                value: float = (
                    node.children[(1, 0, z)].value + node.children[(1, 1, z)].value
                ) / 2
            case Direction.UP:
                # interpolate value
                # from bottommost children
                value: float = (
                    node.children[(0, 1, z)].value + node.children[(1, 1, z)].value
                ) / 2
            case Direction.DOWN:
                # interpolate value
                # from topmost children
                value: float = (
                    node.children[(0, 0, z)].value + node.children[(1, 0, z)].value
                ) / 2

        # the distance between
        # a coarser node a finer
        # neighbor node is 0.75
        return (value, 0.75)


class CustomRefinementCriterium(RefinementCriterium):
    """
    A class used to define a custom refinement criterium.
    """

    def __init__(self, f: Callable[["Node"], bool]) -> None:
        """
        Constructor for the CustomRefinementCriterium class.

            Parameters:
                f (Callable[[Node], bool]): The function that defines the refinement criterium.

            Returns:
                None
        """
        self._f: Callable[["Node"], bool] = f

    def eval(self, node: "Node") -> bool:
        return self._f(node)


class GradientRefinementCriterium(RefinementCriterium):
    """
    A class used to define a gradient refinement criterium.
    It implements a first-order gradient approximation.
    """

    def __init__(self, threshold: float) -> None:
        """
        Constructor for the GradientRefinementCriterium class.

            Parameters:
                threshold (float): The threshold value for the gradient refinement criterium.

            Returns:
                None
        """
        self._threshold: float = threshold

    def eval(self, node: "Node") -> bool:
        # get neighbors' values
        # in all cardinal directions
        neighbors: list[tuple[Optional[float], float]] = reduce(
            lambda res, dd: [
                *res,
                RefinementCriterium.handle_neighbor(node, dd[1], dd[0]),
            ]
            if dd[1] is not None
            else [*res, (None, 0.0)],
            map(
                lambda d: (d, node.neighbor(d)),
                [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN],
            ),
            [],
        )
        # check that every direction
        # has a valid neighbor
        if not all(n[0] for n in neighbors):
            return False

        # destructure into
        # individual nodes
        right_value, right_factor = neighbors[0]
        left_value, left_factor = neighbors[1]
        up_value, up_factor = neighbors[2]
        down_value, down_factor = neighbors[3]

        # compute second order
        # central difference for
        # x-direction gradient
        dx_gradient: float = (right_value - left_value) / (right_factor + left_factor)

        # compute second order
        # central difference for
        # y-direction gradient
        dy_gradient: float = (up_value - down_value) / (up_factor + down_factor)

        # compute gradient magnitude
        # using L2 norm
        gradient_magnitude: float = (dx_gradient**2 + dy_gradient**2) ** 0.5

        # compute relative gradient
        relative_gradient: float = (
            gradient_magnitude / node.value if node.value != 0.0 else 0.0
        )
        node.gradient = relative_gradient

        return relative_gradient > self._threshold


class LogScaleGradientRefinuementCriterium(RefinementCriterium):
    """
    A class used to define a log-scaled gradient refinement criterium.
    It implements a first-order gradient approximation.
    """

    def __init__(self, threshold: float) -> None:
        """
        Constructor for the LogScaleGradientRefinuementCriterium class.

            Parameters:
                threshold (float): The threshold value for the gradient refinement criterium.

            Returns:
                None
        """
        self._threshold: float = threshold

    def eval(self, node: "Node") -> bool:
        # get neighbors' values
        # in all cardinal directions
        neighbors: list[tuple[Optional[float], float]] = reduce(
            lambda res, dd: [
                *res,
                RefinementCriterium.handle_neighbor(node, dd[1], dd[0]),
            ]
            if dd[1] is not None
            else [*res, (None, 0.0)],
            map(
                lambda d: (d, node.neighbor(d)),
                [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN],
            ),
            [],
        )
        # check that every direction
        # has a valid neighbor
        if not all(n[0] for n in neighbors):
            return False

        # destructure into
        # individual nodes
        right_value, right_factor = neighbors[0]
        left_value, left_factor = neighbors[1]
        up_value, up_factor = neighbors[2]
        down_value, down_factor = neighbors[3]

        # compute second order
        # central difference for
        # x-direction gradient
        dx_gradient: float = (right_value - left_value) / (right_factor + left_factor)

        # compute second order
        # central difference for
        # y-direction gradient
        dy_gradient: float = (up_value - down_value) / (up_factor + down_factor)

        # compute gradient magnitude
        # using L2 norm
        gradient_magnitude: float = (dx_gradient**2 + dy_gradient**2) ** 0.5

        # compute relative gradient
        relative_gradient: float = (
            gradient_magnitude / node.value if node.value != 0.0 else 0.0
        )

        # compute logarithm gradient
        relative_gradient = log(relative_gradient + 1)

        # scale gradient
        relative_gradient = relative_gradient * 10.0

        node.gradient = relative_gradient

        return relative_gradient > self._threshold
