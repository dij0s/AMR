from .node import Node, Point


class Tree:
    """
    A class used to create Tree objects.
    """

    def __init__(self) -> None:
        """
        Constructor for the TreeFactory class.

            Returns:
                None
        """
        pass

    def create_root(
        self, value: float, origin_x: int, origin_y: int, origin_z: int = 0
    ) -> Node:
        """
        Creates the root node of a Tree.

            Parameters:
                origin_x (int): The x-coordinate of the origin of the node.
                origin_y (int): The y-coordinate of the origin of the node.
                origin_z (int): The z-coordinate of the origin of the node. By default, it is set to 0 (2D).
                value (float): The value of the node.

            Returns:
                Node: The newly created node.
        """
        origin: Point = (origin_x, origin_y, origin_z)
        return Node(value=value, level=0, origin=origin)
