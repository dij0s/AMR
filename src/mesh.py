from typing import Generator, Union

from .node import Node, Point


class Mesh:
    """
    A class used to create Mesh objects.
    """

    def __init__(self, lx: int, ly: int, lz: int = None) -> None:
        """
        Constructor for the Mesh class.
            Parameters:
                lx (int): Length of the Mesh in the x-direction [-].
                ly (int): Length of the Mesh in the y-direction [-].
                lz (int): Length of the Mesh in the z-direction [-]. If not provided, the Mesh is 2D.

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

    def leafs(self) -> Generator[Node, None, None]:
        """
        Returns a generator of all leaf nodes in the Mesh Tree.

            Returns:
                Generator[Node, None, None]: A generator yielding all leaf nodes in the Mesh Tree.
        """
        if not self._root:
            return

        def collect_leaves(node: Node) -> Generator[Node, None, None]:
            if not node.children:
                yield node
            else:
                for child in node.children:
                    if child:
                        yield from collect_leaves(child)

        yield from collect_leaves(self._root)

    def save(self, filename: str) -> None:
        """
        Save the Mesh Tree to a VTK file.

            Parameters:
                filename (str): The name of the file to save the Mesh Tree.

            Returns:
                None
        """
        if not self._root:
            raise ValueError("Mesh is empty. Cannot save empty mesh.")

        # ensure the filename has .vtk extension
        if not filename.endswith(".vtk"):
            filename += ".vtk"

        # get all leaf nodes
        leaves = list(self.leafs())

        # write VTK file
        with open(filename, "w") as f:
            # write header
            f.write("# vtk DataFile Version 3.0\n")
            f.write("AMR Mesh\n")
            f.write("ASCII\n")
            f.write("DATASET UNSTRUCTURED_GRID\n")

            # write points
            # 4 points per 2D cell, 8 for 3D
            total_points = len(leaves) * (4 if self._lz is None else 8)
            f.write(f"\nPOINTS {total_points} float\n")

            point_count: int = 0
            # maps node origins to point indices
            point_map: dict[Union[tuple[int, int], tuple[int, int, int]], int] = {}

            for leaf in leaves:
                level_size: float = 1 / (2**leaf.level)
                ox, oy = leaf.origin[0], leaf.origin[1]

                # 2D mesh
                if self._lz is None:
                    points = [
                        (ox * level_size, oy * level_size),
                        ((ox + 1) * level_size, oy * level_size),
                        ((ox + 1) * level_size, (oy + 1) * level_size),
                        (ox * level_size, (oy + 1) * level_size),
                    ]

                    for x, y in points:
                        f.write(f"{x} {y} 0\n")
                        point_map[(x, y)] = point_count
                        point_count += 1

                # 3D mesh
                else:
                    oz = leaf.origin[2]
                    points = [
                        (ox * level_size, oy * level_size, oz * level_size),
                        ((ox + 1) * level_size, oy * level_size, oz * level_size),
                        ((ox + 1) * level_size, (oy + 1) * level_size, oz * level_size),
                        (ox * level_size, (oy + 1) * level_size, oz * level_size),
                        (ox * level_size, oy * level_size, (oz + 1) * level_size),
                        ((ox + 1) * level_size, oy * level_size, (oz + 1) * level_size),
                        (
                            (ox + 1) * level_size,
                            (oy + 1) * level_size,
                            (oz + 1) * level_size,
                        ),
                        (ox * level_size, (oy + 1) * level_size, (oz + 1) * level_size),
                    ]

                    for x, y, z in points:
                        f.write(f"{x} {y} {z}\n")
                        point_map[(x, y, z)] = point_count
                        point_count += 1

            # write cells
            num_cells: int = len(leaves)
            points_per_cell: int = 4 if self._lz is None else 8
            f.write(f"\nCELLS {num_cells} {num_cells * (points_per_cell + 1)}\n")

            cell_id: int = 0
            for leaf in leaves:
                level_size: float = 1 / (2**leaf.level)
                ox, oy = leaf.origin[0], leaf.origin[1]

                # 2D mesh
                if self._lz is None:
                    f.write(
                        f"4 {cell_id * 4} {cell_id * 4 + 1} {cell_id * 4 + 2} {cell_id * 4 + 3}\n"
                    )
                # 3D mesh
                else:
                    f.write(
                        f"8 {cell_id * 8} {cell_id * 8 + 1} {cell_id * 8 + 2} {cell_id * 8 + 3} "
                        f"{cell_id * 8 + 4} {cell_id * 8 + 5} {cell_id * 8 + 6} {cell_id * 8 + 7}\n"
                    )
                cell_id += 1

            # write cell types
            f.write(f"\nCELL_TYPES {num_cells}\n")
            # VTK_QUAD = 9, VTK_HEXAHEDRON = 12
            cell_type: int = 9 if self._lz is None else 12
            for _ in range(num_cells):
                f.write(f"{cell_type}\n")

            # write cell data (values)
            f.write(f"\nCELL_DATA {num_cells}\n")
            f.write("SCALARS value float 1\n")
            f.write("LOOKUP_TABLE default\n")
            for leaf in leaves:
                f.write(f"{leaf.value}\n")

    @property
    def root(self) -> Node:
        """
        Returns the root node of the Mesh Tree.

            Returns:
                Node: The root node of the Mesh Tree.
        """
        return self._root
