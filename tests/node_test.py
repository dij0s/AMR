from pytest import fixture

from src.mesh import Mesh
from src.node import Direction, Node
from src.refinement import CustomRefinementCriterium


@fixture
def mesh() -> Node:
    return Mesh(lx=10, ly=10, lz=0)


@fixture
def heterogeneous_mesh() -> Mesh:
    mesh = Mesh(lx=10, ly=10)
    root = mesh.create_root(value=2.0, origin_x=0, origin_y=0)
    refinement_criterium = CustomRefinementCriterium(lambda node: node.value > 1.0)

    # refine at multiple levels
    # to create an heterogeneous mesh
    root.refine(refinement_criterium)
    root.children[(0, 0, None)].refine(refinement_criterium)

    return mesh


def test_node_localization(heterogeneous_mesh):
    """
    Test the localization of a node in the mesh
    geographically using directions
    """
    # check correct mesh creation
    assert len(list(heterogeneous_mesh.leafs())) == 7

    # check the localization of a node
    # from upmost left node
    upmost_left_node = heterogeneous_mesh.root.children[(0, 0, None)].children[
        (0, 0, None)
    ]
    assert upmost_left_node.absolute_origin == (0, 0, None)

    # check localization of top
    # node, must not be found
    # as the node is on border
    top_node = upmost_left_node.neighbor(Direction.UP)
    assert top_node is None

    # check localization of right
    # node, must be found and be
    # a node of same level
    right_node = upmost_left_node.neighbor(Direction.RIGHT)
    assert upmost_left_node.level == right_node.level

    # check localization of bottom
    # node, must be found and be
    # a node of same level
    bottom_node = upmost_left_node.neighbor(Direction.DOWN)
    assert upmost_left_node.level == bottom_node.level

    # check localization of left
    # node, must not be found
    # as the node is on border
    left_node = upmost_left_node.neighbor(Direction.LEFT)
    assert left_node is None

    # now considering the node
    # at the downmost right
    # of the finest mesh
    downmost_right_node = heterogeneous_mesh.root.children[(0, 0, None)].children[
        (1, 1, None)
    ]

    # check localization of top
    # node, must be found and be
    # a node of same level
    top_node = downmost_right_node.neighbor(Direction.UP)
    assert downmost_right_node.level == top_node.level

    # check localization of right
    # node, must be found but be
    # of lower level
    right_node = downmost_right_node.neighbor(Direction.RIGHT)
    assert downmost_right_node.level == right_node.level + 1

    # check localization of bottom
    # node, must be found but be
    # of lower level
    bottom_node = downmost_right_node.neighbor(Direction.DOWN)
    assert downmost_right_node.level == bottom_node.level + 1

    # check localization of left
    # node, must be found and be
    # a node of same level
    left_node = downmost_right_node.neighbor(Direction.LEFT)
    assert downmost_right_node.level == left_node.level

    # now considering the node
    # at the downmost left
    # of the coarses mesh
    downmost_left_node = heterogeneous_mesh.root.children[(0, 1, None)]

    # check localization of left
    # node, must not be found
    # as the node is on border
    left_node = downmost_left_node.neighbor(Direction.LEFT)
    assert left_node is None

    # check localization of bottom
    # node, must not be found
    # as the node is on border
    bottom_node = downmost_left_node.neighbor(Direction.DOWN)
    assert bottom_node is None

    # check localization of right
    # node, must be found and be
    # a node of same level
    right_node = downmost_left_node.neighbor(Direction.RIGHT)
    assert downmost_left_node.level == right_node.level

    # check localization of top
    # node, must be found but be
    # of lower level
    top_node = downmost_left_node.neighbor(Direction.UP)
    assert not top_node.is_leaf()


def test_quadtree_creation(mesh):
    """
    Test the creation of a quadtree root node
    """
    node = mesh.create_root(value=2.0, origin_x=0, origin_y=1)

    assert node.origin == (0, 1, None)
    assert node.level == 0
    assert node.value == 2.0

    assert node.parent is None
    assert node.children == {}
    assert node.is_leaf()

    assert node.absolute_origin == (0, 1, None)


def test_octree_creation(mesh):
    """
    Test the creation of an octree root node
    """
    node = mesh.create_root(value=2.0, origin_x=1, origin_y=1, origin_z=2)

    assert node.origin == (1, 1, 2)
    assert node.level == 0
    assert node.value == 2.0

    assert node.parent is None
    assert node.children == {}
    assert node.is_leaf()

    assert node.absolute_origin == (1, 1, 2)
