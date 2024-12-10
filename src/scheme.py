from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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


class SecondOrderCentral(NumericalScheme):
    """
    A class used to define a second order
    central finite differences numerical scheme.
    """

    def __init__(self, laplacian_factor: float, d1: float, d2: float) -> None:
        """
        Constructor for the SecondOrderCentral class.

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
        nodes_copy: list["Node"] = map(lambda node: node.copy(), nodes)

        # iterate over nodes
        for node, node_copy in zip(nodes, nodes_copy):
            # calculate Laplacian term
            laplacian: float = ()

            # calculate Laplacian term
            # laplacian: float = self._laplacian_factor

            # calculate first derivative term
            d1 = self._d1 * node_copy.d1

            # calculate second derivative term
            d2 = self._d2 * node_copy.d2

            # calculate new value
            node.value = node_copy.value + laplacian + d1 + d2
