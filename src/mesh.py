from .node import Node, Point


class Mesh:
    """
    A class used to create Mesh objects.
    """

    def __init__(self, lx: int, ly: int, lz: int) -> None:
        """
        Constructor for the Mesh class.
            Parameters:
                lx (int): Length of the Mesh in the x-direction [-].
                ly (int): Length of the Mesh in the y-direction [-].
                lz (int): Length of the Mesh in the z-direction [-].

            Returns:
                None
        """
        self._root = None  # Root node of the Mesh Tree

        self._lx = lx
        self._ly = ly
        self._lz = lz

    def create_root(
        self, value: float, origin_x: int, origin_y: int, origin_z: int = None
    ) -> Node:
        """
        Creates the root node of a Mesh Tree.

            Parameters:
                origin_x (int): The x-coordinate of the origin of the node.
                origin_y (int): The y-coordinate of the origin of the node.
                origin_z (int): The z-coordinate of the origin of the node. By default, it is set to None (2D).
                value (float): The value of the node.

            Returns:
                Node: The newly created node.
        """
        origin: Point = (origin_x, origin_y, origin_z)
        self._root = Node(value=value, level=0, origin=origin)

        return self._root

    @property
    def root(self) -> Node:
        """
        Returns the root node of the Mesh Tree.

            Returns:
                Node: The root node of the Mesh Tree.
        """
        return self._root
