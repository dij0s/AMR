from pytest import fixture

from src.node import Node
from src.tree import Tree


@fixture
def tree() -> Node:
    return Tree()


def test_quadtree_creation(tree):
    """
    Test the creation of a quadtree root node
    """
    node = tree.create_root(value=2.0, origin_x=0, origin_y=1)

    assert node.origin == (0, 1, 0)
    assert node.level == 0
    assert node.value == 2.0


def test_octree_creation(tree):
    """
    Test the creation of an octree root node
    """
    node = tree.create_root(value=2.0, origin_x=1, origin_y=1, origin_z=2)

    assert node.origin == (1, 1, 2)
    assert node.level == 0
    assert node.value == 2.0
