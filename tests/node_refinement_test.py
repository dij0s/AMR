from pytest import fixture

from src.mesh import Mesh
from src.node import Node
from src.refinement import CustomRefinementCriterium


@fixture
def mesh() -> Node:
    return Mesh(lx=10, ly=10, lz=0)


@fixture
def custom_refinement_criterium() -> CustomRefinementCriterium:
    return CustomRefinementCriterium(lambda node: node.value > 2.0)


def test_custom_refinement(mesh, custom_refinement_criterium):
    """
    Test the custom refinement criterium on a node
    """
    node_a: Node = mesh.create_root(value=2.0, origin_x=0, origin_y=1)
    assert not node_a.shall_refine(custom_refinement_criterium)

    node_b: Node = mesh.create_root(value=5.0, origin_x=1, origin_y=1)
    assert node_b.shall_refine(custom_refinement_criterium)
