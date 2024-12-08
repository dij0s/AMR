from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

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
