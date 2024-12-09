from pytest import fixture

from src.mesh import Mesh
from src.node import Node


@fixture
def mesh() -> Node:
    return Mesh(lx=10, ly=10, lz=0)


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
