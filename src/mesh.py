from typing import Generator

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

    def uniform(self, n: int, leaf_value: float) -> Node:
        """
        Create a 2D Mesh Tree of defined size.

            Parameters:
                n (int): The number of nodes in the Mesh Tree (in a single dimension).
                leaf_value (float): The value to be assigned to the leaf nodes.

            Returns:
                Node: The root node of the Mesh Tree.
        """

        # check that the provided
        # number of nodes is valid
        # (must be a power of 2)
        if n & (n - 1) != 0:
            raise ValueError("Number of nodes must be a power of 2.")
        else:
            n_refinements: int = n.bit_length() - 1

        # create the root node
        origin: Point = (0, 0, None)
        self._root = Node(value=leaf_value, level=0, origin=origin)

        # refine the leaf nodes
        # at each and every step
        to_refine: list[Node] = [self._root]
        while n_refinements > 0:
            new_to_refine: list[Node] = []
            for node in to_refine:
                node.refine()
                new_to_refine.extend(node.children.values())
            to_refine = new_to_refine
            n_refinements -= 1

        return self._root

    def create_root(
        self, value: float, origin_x: int, origin_y: int, origin_z: int = None
    ) -> Node:
        """
        Creates the root node of a Mesh Tree.

            Parameters:
                value (float): The value of the node.
                origin_x (int): The x-coordinate of the origin of the node.
                origin_y (int): The y-coordinate of the origin of the node.
                origin_z (int): The z-coordinate of the origin of the node. By default, it is set to None (2D).

            Returns:
                Node: The newly created node.
        """
        origin: Point = (origin_x, origin_y, origin_z)
        self._root = Node(value=value, level=0, origin=origin)

        return self._root

    def leafs(self) -> Generator[Node, None, None]:
        if not self._root:
            raise ValueError("Mesh is empty. Cannot get leafs of empty mesh.")

        yield from self._root.leafs()

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
        leaves: list[Node] = list(self.leafs())
        # n×n grid (2D) or n×n×n grid (3D)
        n: int = int(len(leaves) ** (1 / 2 if self._lz is None else 1 / 3))
        print(
            f"[LOG] Number of leaves: {len(leaves)} ({n}×{n}{f'×{n}' if self._lz is not None else ''} grid)"
        )

        # calculate grid spacing
        dx: float = self._lx / n
        dy: float = self._ly / n
        dz: float = self._lz / n if self._lz is not None else 0

        # generate all grid points
        # maps (x,y) or (x, y, z)
        # to point index
        points: list[Point] = []
        point_indices: dict[tuple[int, int], int] = {}

        if self._lz is None:
            # 2D mesh, generate (n+1)×(n+1)
            # points for n² cells
            for j in range(n + 1):
                for i in range(n + 1):
                    x: float = i * dx
                    y: float = j * dy
                    points.append((x, y, 0))
                    point_indices[(i, j)] = len(points) - 1
        else:
            # 3D mesh, generate (n+1)×(n+1)×(n+1)
            # points for n³ cells
            for k in range(n + 1):
                for j in range(n + 1):
                    for i in range(n + 1):
                        x: float = i * dx
                        y: float = j * dy
                        z: float = k * dz
                        points.append((x, y, z))
                        point_indices[(i, j, k)] = len(points) - 1

        # write VTK file in output directory
        with open(f"output/{filename}", "w") as f:
            print(f"[LOG] Writing VTK file: {filename}...")

            # write header
            f.write("# vtk DataFile Version 3.0\n")
            f.write("AMR Mesh\n")
            f.write("ASCII\n")
            f.write("DATASET UNSTRUCTURED_GRID\n")

            # write points
            f.write(f"\nPOINTS {len(points)} float\n")
            for x, y, z in points:
                f.write(f"{x} {y} {z}\n")

            # write cells
            num_cells: int = n**2 if self._lz is None else n**3
            points_per_cell: int = 4 if self._lz is None else 8
            f.write(f"\nCELLS {num_cells} {num_cells * (points_per_cell + 1)}\n")

            if self._lz is None:
                # 2D mesh, generate quad cells
                for j in range(n):
                    for i in range(n):
                        # get the four corner
                        # points of each cell
                        p0: int = point_indices[(i, j)]
                        p1: int = point_indices[(i + 1, j)]
                        p2: int = point_indices[(i + 1, j + 1)]
                        p3: int = point_indices[(i, j + 1)]
                        f.write(f"4 {p0} {p1} {p2} {p3}\n")
            else:
                # 3D mesh, generate hexahedron cells
                for k in range(n):
                    for j in range(n):
                        for i in range(n):
                            # get the eight corner
                            # points of each cell
                            p0: int = point_indices[(i, j, k)]
                            p1: int = point_indices[(i + 1, j, k)]
                            p2: int = point_indices[(i + 1, j + 1, k)]
                            p3: int = point_indices[(i, j + 1, k)]
                            p4: int = point_indices[(i, j, k + 1)]
                            p5: int = point_indices[(i + 1, j, k + 1)]
                            p6: int = point_indices[(i + 1, j + 1, k + 1)]
                            p7: int = point_indices[(i, j + 1, k + 1)]
                            f.write(f"8 {p0} {p1} {p2} {p3} {p4} {p5} {p6} {p7}\n")

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
