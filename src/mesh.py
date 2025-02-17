import os
from typing import Callable, Generator, Optional

from .benchmark import Benchmark
from .node import Node, Point
from .refinement import CustomRefinementCriterium, RefinementCriterium
from .scheme import NumericalScheme

# get the benchmark instance
benchmark = Benchmark()


class Mesh:
    """
    A class used to create Mesh objects.
    """

    def __init__(self, lx: float, ly: float, lz: Optional[float] = None) -> None:
        """
        Constructor for the Mesh class.
            Parameters:
                lx (float): Length of the Mesh in the x-direction [m].
                ly (float): Length of the Mesh in the y-direction [m].
                lz (Optional[float]): Length of the Mesh in the z-direction [m]. If not provided, the Mesh is 2D.

            Returns:
                None
        """
        self._root: Optional[Node] = None

        self._lx: float = lx
        self._ly: float = ly
        self._lz: Optional[float] = lz

    @staticmethod
    def uniform(
        n: int,
        leaf_value: Callable[[], float],
        lx: float,
        ly: float,
        lz: Optional[float] = None,
    ) -> tuple["Mesh", int]:
        """
        Create a Mesh Tree of uniform size.

            Parameters:
                n (int): The number of nodes in the Mesh Tree (per dimension).
                leaf_value (Callable[float, None, None]): The function to apply to generate the value of the leaf nodes.
                lx (float): Length of the Mesh in the x-direction [m].
                ly (float): Length of the Mesh in the y-direction [m].
                lz (Optional[float]): Length of the Mesh in the z-direction [m]. If not provided, the Mesh is 2D.

            Returns:
                Mesh: The uniform Mesh Tree.
                int: The maximal leaf level of the Mesh Tree.
        """
        mesh: Mesh = Mesh(lx=lx, ly=ly, lz=lz)

        # check that the provided
        # number of nodes is valid
        # (must be a power of 2)
        if n & (n - 1) != 0:
            raise ValueError("Number of nodes must be a power of 2.")
        else:
            n_refinements: int = n.bit_length() - 1

        # create the root node
        origin: Point = (0, 0, 0 if lz else None)
        mesh._root = Node(value=0, level=0, origin=origin)

        # create copy of number of refinements
        # to keep track of the leaf level
        maximal_leaf_level: int = n_refinements

        # refine the leaf nodes
        # at each and every step
        # to create a uniform mesh
        to_refine: list[Node] = [mesh._root]
        while n_refinements > 0:
            new_to_refine: list[Node] = []

            # refine current nodes
            for node in to_refine:
                node.refine(number_generator=leaf_value)
                new_to_refine.extend(node.children.values())

            # update the members to
            # refine the children
            # of the current nodes
            to_refine = new_to_refine

            n_refinements -= 1

        return mesh, maximal_leaf_level

    def create_root(
        self, value: float, origin_x: int, origin_y: int, origin_z: Optional[int] = None
    ) -> Node:
        """
        Creates the root node of a Mesh Tree.

            Parameters:
                value (float): The value of the node.
                origin_x (int): The x-coordinate of the origin of the node.
                origin_y (int): The y-coordinate of the origin of the node.
                origin_z (Optional[int]): The z-coordinate of the origin of the node. By default, it is set to None (2D).

            Returns:
                Node: The newly created node.
        """
        origin: Point = (origin_x, origin_y, origin_z)
        self._root = Node(value=value, level=0, origin=origin)

        return self._root

    @benchmark.time
    @benchmark.space
    def refine(
        self,
        criterium: RefinementCriterium,
        min_depth: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> None:
        """
        Refine and coarsen the Mesh Tree based on a refinement criterium.

            Parameters:
                criterium (RefinementCriterium): The refinement criterium.
                min_depth (Optional[int]): The minimal absolute depth of the Mesh Tree. By default, it is set to None but it should absolutely be set.
                max_depth (Optional[int]): The maximal absolute depth of the Mesh Tree. By default, it is set to None but it should absolutely be set.

            Returns:
                None
        """
        if not self._root:
            raise ValueError("Mesh is empty. Cannot refine empty mesh.")

        # get all leaf nodes
        leaves: list[Node] = list(self.leafs())

        # create bypass criterium
        # for stripe refinement
        # and only physical
        # constraints checking
        bypass_criterium: RefinementCriterium = CustomRefinementCriterium(
            lambda node: True
        )

        # first pass, identify leaf
        # nodes that need refinement
        to_refine: set[Node] = set()
        neighbors: set[Node] = set()
        for leaf in leaves:
            # only evaluate criterium
            # refinement condition as
            # buffer zone is refined
            # before and may lead
            # to further refinement
            # because of mesh grading
            # constraints
            if criterium.eval(leaf):
                for node in leaf.buffer(4):
                    # refine buffer nodes
                    # that satisfy the
                    # physical constraints
                    if leaf.level < max_depth and (
                        node
                        and node.is_leaf()
                        and node.level < max_depth
                        and node.shall_refine(bypass_criterium)
                    ):
                        # neighbors are added to
                        # the set to avoid coarsening
                        # them if they are in the
                        # interest zone of the leaf
                        neighbors.add(node)
                        node.refine()
                    else:
                        # if neighbor is node
                        # refined because of
                        # physical constraints
                        # then make sure that
                        # its parent does not
                        # get coarsened as it
                        # would lead to loss
                        # of information near
                        # the leaf node
                        neighbors.add(node.parent)

                # add current node
                # to refinement set
                # only if previous
                # buffer refinement
                # allows current leaf
                # physical constraints
                # being met
                if leaf.shall_refine(criterium) and leaf.level < max_depth:
                    to_refine.add(leaf)

        # refine the identified nodes
        for node in to_refine:
            node.refine()

        # get updated leaf nodes
        # after the first pass
        leaves = list(self.leafs())

        # second pass, collect all parents
        # that might need coarsening
        # group siblings together
        # by their parent
        parent_children: dict[Node, list[Node]] = {}
        for leaf in leaves:
            parent: Optional[Node] = leaf.parent
            # exclude parent of leaf
            # nodes that were refined
            # in the first pass
            if parent not in to_refine.union(neighbors):
                if parent not in parent_children:
                    parent_children[parent] = []
                parent_children[parent].append(leaf)

        # check which parents
        # can be coarsened
        to_coarsen: list[Node] = []
        for parent, children in parent_children.items():
            # only consider parents where
            # all children are leaves and
            # not marked for refinement
            if all(child.is_leaf() for child in children) and len(children) == (
                8 if parent._is_tri_dimensional else 4
            ):
                # check if coarsening is allowed
                # based on neighbor levels
                if parent.shall_coarsen(criterium) and parent.level >= min_depth:
                    to_coarsen.append(parent)

        # coarsen the identified nodes
        for node in to_coarsen:
            node.coarsen()

    @benchmark.time
    @benchmark.space
    def inject(self, f: Callable[[Node], None]) -> None:
        """
        Inject a function into the Mesh Tree. It is applied to each node of the Mesh Tree recursively.

            Parameters:
                f (Callable[[Node], None]): The function to inject into the Mesh Tree.

            Returns:
                None
        """
        if not self._root:
            raise ValueError("Mesh is empty. Cannot inject function into empty mesh.")

        self._root.inject(f)

    @benchmark.time
    @benchmark.space
    def solve(self, scheme: NumericalScheme) -> None:
        """
        Solve the Mesh Tree using a numerical scheme.

            Parameters:
                scheme (NumericalScheme): The numerical scheme to solve the Mesh Tree.

            Returns:
                None
        """
        if not self._root:
            raise ValueError("Mesh is empty. Cannot solve empty mesh.")

        # solver shall be applied
        # to the list of leaf nodes
        scheme.apply(list(self.leafs()))

    def leafs(self) -> Generator[Node, None, None]:
        if not self._root:
            raise ValueError("Mesh is empty. Cannot get leafs of empty mesh.")

        yield from self._root.leafs()

    @benchmark.time
    @benchmark.space
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

        # ensure the filename
        # has .vtk extension
        if not filename.endswith(".vtk"):
            filename += ".vtk"

        # ensure that the output
        # directory exists
        if not os.path.exists("output"):
            os.makedirs("output")

        # get all leaf nodes
        leaves: list[Node] = list(self.leafs())
        print(f"{len(leaves)} leaf nodes must be written into the file.")

        # Create points dictionary to avoid duplicates
        points: list[Point] = []
        point_indices: dict[Point, int] = {}
        cells: list[tuple] = []

        for leaf in leaves:
            # compute cell size
            # based on level
            cell_size_x: float = self._lx / (2**leaf.level)
            cell_size_y: float = self._ly / (2**leaf.level)
            cell_size_z: float = (
                self._lz / (2**leaf.level) if self._lz is not None else 0
            )

            # Scale the origin to actual dimensions
            scaled_origin: Point = (
                leaf.absolute_origin[0] * self._lx,
                leaf.absolute_origin[1] * self._ly,
                leaf.absolute_origin[2] * self._lz
                if self._lz is not None and leaf.absolute_origin[2] is not None
                else 0,
            )

            if self._lz is None:
                # 2D mesh
                # compute the four
                # corners of the cell
                corners: list[Point] = [
                    (scaled_origin[0], scaled_origin[1], 0),
                    (scaled_origin[0] + cell_size_x, scaled_origin[1], 0),
                    (scaled_origin[0] + cell_size_x, scaled_origin[1] + cell_size_y, 0),
                    (scaled_origin[0], scaled_origin[1] + cell_size_y, 0),
                ]

                # get or create
                # point indices
                cell_points: list[int] = []
                for corner in corners:
                    if corner not in point_indices:
                        points.append(corner)
                        point_indices[corner] = len(points) - 1
                    cell_points.append(point_indices[corner])

                cells.append(tuple(cell_points))

            else:
                # 3D mesh
                # compute the eight
                # corners of the cell
                corners: list[Point] = [
                    (scaled_origin[0], scaled_origin[1], scaled_origin[2]),
                    (
                        scaled_origin[0] + cell_size_x,
                        scaled_origin[1],
                        scaled_origin[2],
                    ),
                    (
                        scaled_origin[0] + cell_size_x,
                        scaled_origin[1] + cell_size_y,
                        scaled_origin[2],
                    ),
                    (
                        scaled_origin[0],
                        scaled_origin[1] + cell_size_y,
                        scaled_origin[2],
                    ),
                    (
                        scaled_origin[0],
                        scaled_origin[1],
                        scaled_origin[2] + cell_size_z,
                    ),
                    (
                        scaled_origin[0] + cell_size_x,
                        scaled_origin[1],
                        scaled_origin[2] + cell_size_z,
                    ),
                    (
                        scaled_origin[0] + cell_size_x,
                        scaled_origin[1] + cell_size_y,
                        scaled_origin[2] + cell_size_z,
                    ),
                    (
                        scaled_origin[0],
                        scaled_origin[1] + cell_size_y,
                        scaled_origin[2] + cell_size_z,
                    ),
                ]

                # get or create
                # point indices
                cell_points: list[int] = []
                for corner in corners:
                    if corner not in point_indices:
                        points.append(corner)
                        point_indices[corner] = len(points) - 1
                    cell_points.append(point_indices[corner])

                cells.append(tuple(cell_points))

        # write the VTK file
        with open(f"output/{filename}", "w") as f:
            print(f"Saving Mesh data into file {filename}...")

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
            points_per_cell = 4 if self._lz is None else 8
            f.write(f"\nCELLS {len(cells)} {len(cells) * (points_per_cell + 1)}\n")
            for cell in cells:
                f.write(f"{points_per_cell} {' '.join(map(str, cell))}\n")

            # write cell types
            f.write(f"\nCELL_TYPES {len(cells)}\n")
            # VTK_QUAD = 9, VTK_HEXAHEDRON = 12
            cell_type = 9 if self._lz is None else 12
            for _ in range(len(cells)):
                f.write(f"{cell_type}\n")

            # write cell data (values and gradients)
            f.write(f"\nCELL_DATA {len(cells)}\n")

            f.write("SCALARS value float 1\n")
            f.write("LOOKUP_TABLE default\n")
            for leaf in leaves:
                f.write(f"{leaf.value}\n")

            f.write("SCALARS gradient float 1\n")
            f.write("LOOKUP_TABLE default\n")
            for leaf in leaves:
                f.write(f"{leaf.gradient}\n")

            print("VTK file written successfully.")

    @property
    def root(self) -> Optional[Node]:
        """
        Returns the root node of the Mesh Tree.

            Returns:
                Optional[Node]: The root node of the Mesh Tree.
        """
        return self._root
