from pytest import fixture

from src.node import Node
from src.refinement import CustomRefinementCriterium
from src.tree import Tree


@fixture
def tree() -> Node:
    return Tree()


@fixture
def custom_refinement_criterium() -> CustomRefinementCriterium:
    return CustomRefinementCriterium(lambda node: node.value > 2.0)


def test_custom_refinement(tree, custom_refinement_criterium):
    """
    Test the custom refinement criterium on a node
    """
    node_a: Node = tree.create_root(value=2.0, origin_x=0, origin_y=1)
    assert not node_a.shall_refine(custom_refinement_criterium)

    node_b: Node = tree.create_root(value=5.0, origin_x=1, origin_y=1)
    assert node_b.shall_refine(custom_refinement_criterium)
