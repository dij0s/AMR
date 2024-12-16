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


def test_node_refinement(mesh):
    """
    Test the refinement of a node with and without
    a custom number generator
    """
    # create root node
    node = mesh.create_root(value=2.0, origin_x=0, origin_y=0)

    # test basic refinement
    # with interpolation
    node.refine()
    assert len(node.children) == 4  # for 2D mesh
    assert not node.is_leaf()

    # test refinement with
    # custom number generator
    node2 = mesh.create_root(value=2.0, origin_x=1, origin_y=1)
    node2.refine(number_generator=lambda: 1.0)
    assert all(child.value == 1.0 for child in node2.children.values())


def test_node_coarsening(heterogeneous_mesh):
    """
    Test the coarsening of a node and verify
    the resulting values and structure
    """
    # get a refined node
    refined_node = heterogeneous_mesh.root.children[(0, 0, None)]
    initial_value = refined_node.value

    # coarsen the node
    refined_node.coarsen()
    assert refined_node.is_leaf()
    assert len(refined_node.children) == 0
    # value should be preserved
    assert refined_node.value == initial_value


def test_node_copy(mesh):
    """
    Test the copying of a leaf node and verify
    that copying non-leaf nodes raises an error
    """
    # create and copy
    # a leaf node
    leaf_node = mesh.create_root(value=2.0, origin_x=0, origin_y=0)
    copied_node = leaf_node.copy()

    assert copied_node.value == leaf_node.value
    assert copied_node.level == leaf_node.level
    assert copied_node.origin == leaf_node.origin

    # refine the node
    # and try to copy it
    leaf_node.refine()
    try:
        leaf_node.copy()
        assert False, "should raise ValueError"
    except ValueError:
        assert True


def test_node_injection(mesh):
    """
    Test the injection of a function throughout
    the node hierarchy
    """
    # create a node and
    # refine it
    node = mesh.create_root(value=2.0, origin_x=0, origin_y=0)
    node.refine()

    # inject a function
    # that doubles the value
    def double_value(n):
        n.value = n.value * 2

    node.inject(double_value)

    # check if values were modified
    assert node.value == 4.0
    assert all(child.value == 4.0 for child in node.children.values())


def test_node_absolute_origin(heterogeneous_mesh):
    """
    Test the computation of absolute origins
    for nodes at different levels
    """
    # get nodes at different levels
    root = heterogeneous_mesh.root
    level1_node = root.children[(0, 0, None)]
    level2_node = level1_node.children[(0, 0, None)]

    # check absolute origins
    assert root.absolute_origin == (0, 0, None)
    assert level1_node.absolute_origin == (0, 0, None)
    # level 2 node should have
    # scaled coordinates
    assert level2_node.absolute_origin == (0, 0, None)


def test_shall_refine_coarsen(heterogeneous_mesh):
    """
    Test the refinement and coarsening conditions
    considering neighbor levels
    """
    from src.refinement import CustomRefinementCriterium

    # create a simple criterium
    criterium = CustomRefinementCriterium(lambda node: node.value > 1.0)

    # test refinement condition
    node = heterogeneous_mesh.root.children[(0, 0, None)]
    can_refine = node.shall_refine(criterium)

    # test coarsening condition
    node = heterogeneous_mesh.root.children[(0, 0, None)]
    can_coarsen = node.shall_coarsen(criterium)

    # both conditions shouldn't
    # be true simultaneously
    assert not (can_refine and can_coarsen)


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


def test_node_absolute_centered_origin(heterogeneous_mesh):
    """
    Test the computation of absolute centered origins
    for nodes at different levels. Unlike absolute_origin,
    centered origins account for cell centers.
    """
    # get nodes at different levels
    root = heterogeneous_mesh.root
    level1_node = root.children[(0, 0, None)]
    level2_node = level1_node.children[(0, 0, None)]

    # check absolute centered origins
    # root node should have same
    # centered and regular origin
    assert root.absolute_centered_origin == (0.5, 0.5, None)

    # level 1 node should have
    # centered coordinates scaled
    # by 1/2 and offset by parent
    assert level1_node.absolute_centered_origin == (0.25, 0.25, None)

    # level 2 node should have
    # centered coordinates scaled
    # by 1/4 and offset by parent
    assert level2_node.absolute_centered_origin == (0.125, 0.125, None)


def test_node_chain_localization(heterogeneous_mesh):
    """
    Test the localization of a node in the mesh
    by chaining the directions
    """
    # get topmost left node
    topmost_left = heterogeneous_mesh.root.children[(0, 0, None)].children[(0, 0, None)]
    assert topmost_left is not None

    # get the node on the
    # bottom right
    # it should be of same
    # level as current node
    bottom_right = topmost_left.chain(Direction.DOWN, Direction.RIGHT)
    assert bottom_right is not None
    assert topmost_left.level == bottom_right.level

    # get the node on the
    # absolute bottom right
    # it should be of lower
    # level than current node
    # as it is coarser
    absolute_bottom_right = bottom_right.chain(Direction.DOWN, Direction.RIGHT)
    assert absolute_bottom_right is not None
    assert bottom_right.level == absolute_bottom_right.level + 1

    # there shall be no node
    # when chaining to the bottom
    # right from the absolute
    # bottom right node
    assert absolute_bottom_right.chain(Direction.DOWN, Direction.RIGHT) is None


def test_node_buffer_zone():
    """
    Test the retrieval of a buffer zone
    around a given Node in a Mesh.
    """

    # create mesh of size 8x8
    # which implies three levels
    # of refinement
    mesh, absolute_leaf_level = Mesh.uniform(
        n=8, leaf_value=lambda: 2.0, lx=10.0, ly=10.0
    )

    # get one of the central
    # nodes at the finest level
    node = (
        mesh.root.children[(0, 0, None)].children[(1, 1, None)].children[(1, 1, None)]
    )
    assert node is not None
    assert node.level == absolute_leaf_level

    # get a buffer zone
    # around the node
    buffer_zone = node.buffer(n=3)
    # a buffer zone of size 3
    # yields a square of size 7x7
    # which contains 48 nodes
    # when not considering the
    # current node
    assert len(buffer_zone) == 48

    # get one of the corner-most
    # nodes at the finest level
    node = (
        mesh.root.children[(0, 0, None)].children[(0, 0, None)].children[(0, 0, None)]
    )
    assert node is not None
    assert node.level == absolute_leaf_level

    # get a buffer zone
    # around the node
    buffer_zone = node.buffer(n=3)
    # a buffer zone of size 3
    # based on the corner-most
    # mesh yields a single square
    # of size 4x4 as other nodes
    # are not present and contains
    # 15 nodes when not considering
    # the current node
    assert len(buffer_zone) == 15
