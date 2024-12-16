from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from .node import Direction

if TYPE_CHECKING:
    from .node import Node


class NumericalScheme(ABC):
    """
    This class is used to define a numerical scheme.
    """

    @abstractmethod
    def apply(self, nodes: list["Node"]) -> None:
        """
        Applies the numerical scheme for a list of Node objects.
        """
        pass


class SecondOrderCenteredFiniteDifferences(NumericalScheme):
    """
    A class used to define a second order
    centered finite differences numerical scheme.
    """

    def __init__(
        self,
        laplacian_factor: float,
        d1: float,
        d2: float,
    ) -> None:
        """
        Constructor for the SecondOrderCenteredFiniteDifferences class.

            Parameters:
                laplacian_factor (float): The factor of the Laplacian term.
                d1 (float): The first derivative factor.
                d2 (float): The second derivative factor.

            Returns:
                None
        """
        self._laplacian_factor: float = laplacian_factor
        self._d1: float = d1
        self._d2: float = d2

    def apply(self, nodes: list["Node"]) -> None:
        # create copy of nodes
        nodes_copy: list["Node"] = [node.copy() for node in nodes]

        # iterate over nodes
        for node, node_copy in zip(nodes, nodes_copy):
            # get neighbor nodes
            right: Optional["Node"] = node_copy.neighbor(Direction.RIGHT)
            left: Optional["Node"] = node_copy.neighbor(Direction.LEFT)
            up: Optional["Node"] = node_copy.neighbor(Direction.UP)
            down: Optional["Node"] = node_copy.neighbor(Direction.DOWN)

            # implement a Neumann boundary
            # condition as we specify the
            # derivative (gradient) at the
            # boundary to be zero
            right_value: float = right.value if right else node_copy.value
            left_value: float = left.value if left else node_copy.value
            up_value: float = up.value if up else node_copy.value
            down_value: float = down.value if down else node_copy.value

            # compute the Laplacian term
            # in direction d1
            laplacian_term: float = (
                right_value - (2 * node_copy.value) + left_value
            ) / self._d1**2

            # add the Laplacian term
            # in direction d2
            laplacian_term += (
                up_value - (2 * node_copy.value) + down_value
            ) / self._d2**2

            # multiply the Laplacian term
            # by the Laplacian factor
            laplacian_term = laplacian_term * self._laplacian_factor

            # update the value of the node
            node.value = node_copy.value + laplacian_term
