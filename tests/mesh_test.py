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

        # check that the value of the node is the average of the children values
        assert node.value == sum(c.value for c in node.children.values()) / 4

        # check that the children are leaves
        assert all(c.is_leaf() for c in node.children.values())

        # check that the children are at the next level
        assert all(c.level == node.level + 1 for c in node.children.values())

        # check that the children all reference the same parent node
        assert all(c.parent == node for c in node.children.values())

        # check that the children can access their neighbors
        child: Node = node.children[(0, 0, None)]
        assert child.neighbor((0, 1, None)) is not None
        assert child.neighbor((1, 0, None)) is not None
        assert child.neighbor((1, 1, None)) is not None


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

        # check that the value of the node is the average of the children values
        assert node.value == sum(c.value for c in node.children.values()) / 8

        # check that the children are leaves
        assert all(c.is_leaf() for c in node.children.values())

        # check that the children are at the next level
        assert all(c.level == node.level + 1 for c in node.children.values())

        # check that the children all reference the same parent node
        assert all(c.parent == node for c in node.children.values())

        # check that the children can access their neighbors
        child: Node = node.children[(0, 0, 0)]
        assert child.neighbor((0, 0, 1)) is not None
        assert child.neighbor((0, 1, 0)) is not None
        assert child.neighbor((1, 0, 0)) is not None
        assert child.neighbor((0, 1, 1)) is not None
        assert child.neighbor((1, 0, 1)) is not None
        assert child.neighbor((1, 1, 0)) is not None
        assert child.neighbor((1, 1, 1)) is not None
