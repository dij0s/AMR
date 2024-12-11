from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from src.node import Direction

if TYPE_CHECKING:
    from src.node import Node


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
    """

    def __init__(self, threshold: float) -> None:
        """
        Constructor for the GradientRefinementCriterium class.

            Parameters:
                threshold (float): The threshold value for the gradient refinement criterium. Value between 0 and 1 representing the percentage as decimal (e.g., 0.8 = 80%).

            Returns:
                None
        """
        self._threshold: float = threshold

    def eval(self, node: "Node") -> bool:
        # compute the gradient
        # of the given node

        # get neighboring nodes
        # in all directions
        neighbors: list["Node"] = [
            node.neighbor(Direction.RIGHT),
            node.neighbor(Direction.LEFT),
            node.neighbor(Direction.UP),
            node.neighbor(Direction.DOWN),
        ]

        # filter out None neighbors
        valid_neighbors: list["Node"] = [n for n in neighbors if n is not None]
        if not valid_neighbors:
            return False

        # compute maximum gradient
        # between node and its neighbors
        max_gradient: float = max(
            abs(node.value - neighbor.value) for neighbor in valid_neighbors
        )

        # compute relative gradient
        # node's value is handled to
        # avoid division by zero
        relative_gradient: float = abs(max_gradient / max(node.value, 1e-6))

        # return if absolute
        # percentage gradient
        # exceeds threshold
        return relative_gradient > self._threshold
