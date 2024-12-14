from pytest import fixture

from src.mesh import Mesh
from src.node import Node
from src.refinement import CustomRefinementCriterium


@fixture
def two_dimensional_mesh() -> Mesh:
    return Mesh(lx=10, ly=10)


@fixture
def tri_dimensional_mesh() -> Mesh:
    return Mesh(lx=10, ly=10, lz=10)


@fixture
def custom_refinement_criterium() -> CustomRefinementCriterium:
    return CustomRefinementCriterium(lambda node: node.value > 2.0)


def test_defined_mesh_creation(two_dimensional_mesh):
    """
    Create a 2D mesh of defined number of nodes.
    """
    # create the "pre-refined" mesh
    N: int = 4
    LX: float = 10.0
    LY: float = 10.0
    DX: float = LX / N
    DY: float = LX / N

    mesh, _ = Mesh.uniform(n=N, leaf_value=lambda: 4.0, lx=LX, ly=LY)

    # check that the refinement created
    # the correct number of nodes in each
    # direction (2d mesh of 4x4 nodes)
    assert len(list(mesh.leafs())) == 16

    # check that the mesh is
    # split into 3 levels (0 is base)
    assert all(n.level == 2 for n in mesh.leafs())

    # inject 1 into the mesh if
    # the node is a leaf and else 0
    def f(node: Node) -> None:
        node.value = 1 if node.is_leaf() else 0

    mesh.inject(f)

    # check that the value of
    # all the leaf nodes is 1
    assert all(n.value == 1 for n in mesh.leafs())


def test_two_dimensional_mesh_refinement(
    two_dimensional_mesh, custom_refinement_criterium
):
    """
    Refine a node in the 2D mesh according to a custom refinement criterium.
    """

    # create a root node in a two-dimensional mesh
    node: Node = two_dimensional_mesh.create_root(value=4.0, origin_x=0, origin_y=0)
    shall_refine: bool = node.shall_refine(custom_refinement_criterium)

    # node is not yet refined, it should be a leaf
    assert node.is_leaf()

    if shall_refine:
        node.refine()

        # node is refined, it should not be
        # a leaf as it should have children
        assert not node.is_leaf()

        # check that the node has 4 children
        assert len(node.children) == 4

        # check that the children are leaves
        assert all(c.is_leaf() for c in node.children.values())

        # check that the children are at the next level
        assert all(c.level == node.level + 1 for c in node.children.values())

        # check that the children all reference the same parent node
        assert all(c.parent == node for c in node.children.values())

        # check that the children can access their neighbors
        child: Node = node.children[(0, 0, None)]
        assert child.adjacent((0, 1, None)) is not None
        assert child.adjacent((1, 0, None)) is not None
        assert child.adjacent((1, 1, None)) is not None

        # check that the children have the correct absolute origins
        assert node.children[(0, 0, None)].absolute_origin == (0, 0, None)
        assert node.children[(0, 1, None)].absolute_origin == (0, 0.5, None)
        assert node.children[(1, 0, None)].absolute_origin == (0.5, 0, None)
        assert node.children[(1, 1, None)].absolute_origin == (0.5, 0.5, None)


def test_tri_dimensional_mesh_refinement(
    tri_dimensional_mesh, custom_refinement_criterium
):
    """
    Refine a node in the 3D mesh according to a custom refinement criterium.
    """
    # create a root node in a two-dimensional mesh
    node: Node = tri_dimensional_mesh.create_root(
        value=4.0, origin_x=0, origin_y=0, origin_z=0
    )
    shall_refine: bool = node.shall_refine(custom_refinement_criterium)

    # node is not yet refined, it should be a leaf
    assert node.is_leaf()

    if shall_refine:
        node.refine()

        # node is refined, it should not be
        # a leaf as it should have children
        assert not node.is_leaf()

        # check that the node has 8 children
        assert len(node.children) == 8

        # check that the children are leaves
        assert all(c.is_leaf() for c in node.children.values())

        # check that the children are at the next level
        assert all(c.level == node.level + 1 for c in node.children.values())

        # check that the children all reference the same parent node
        assert all(c.parent == node for c in node.children.values())

        # check that the children can access their neighbors
        child: Node = node.children[(0, 0, 0)]
        assert child.adjacent((0, 0, 1)) is not None
        assert child.adjacent((0, 1, 0)) is not None
        assert child.adjacent((1, 0, 0)) is not None
        assert child.adjacent((0, 1, 1)) is not None
        assert child.adjacent((1, 0, 1)) is not None
        assert child.adjacent((1, 1, 0)) is not None
        assert child.adjacent((1, 1, 1)) is not None

        # check that the children have the correct absolute origins
        assert node.children[(0, 0, 0)].absolute_origin == (0, 0, 0)
        assert node.children[(0, 0, 1)].absolute_origin == (0, 0, 0.5)
        assert node.children[(0, 1, 0)].absolute_origin == (0, 0.5, 0)
        assert node.children[(1, 0, 0)].absolute_origin == (0.5, 0, 0)
        assert node.children[(0, 1, 1)].absolute_origin == (0, 0.5, 0.5)
        assert node.children[(1, 0, 1)].absolute_origin == (0.5, 0, 0.5)
        assert node.children[(1, 1, 0)].absolute_origin == (0.5, 0.5, 0)
        assert node.children[(1, 1, 1)].absolute_origin == (0.5, 0.5, 0.5)


def test_mesh_coarsening(custom_refinement_criterium):
    """
    Coarsen a node in the 2D mesh.
    """
    mesh, _ = Mesh.uniform(n=2, leaf_value=lambda: 1.0, lx=10, ly=10)

    # get the upmost left node
    node = mesh.root.children[(0, 0, None)]

    # check that the node shall coarsen
    # as its neighbors all have the same value
    assert node.shall_coarsen(custom_refinement_criterium)

    mesh.root.children[(1, 0, None)].refine()

    # check that the upmost right
    # node has been refined
    assert not mesh.root.children[(1, 0, None)].is_leaf()
