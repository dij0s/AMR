from src.mesh import Mesh
from src.node import Node
from src.refinement import CustomRefinementCriterium

# create uniform mesh
mesh = Mesh.uniform(n=128, lx=10, ly=10, leaf_value=0.0)


# inject values into tree
# to represent square source
# of heat
def f(node: Node) -> None:
    x, y, _ = node.absolute_origin

    if x > 0.4 and x < 0.6 and y > 0.4 and y < 0.6:
        node.value = 5.0


mesh.inject(f)

mesh.save("mesh_t0.vtk")

# refine mesh based
# on custom criterium

# attention, shall implement better criterium
# that takes into account the difference
# in level with neighboring nodes
criterium = CustomRefinementCriterium(lambda node: node.value > 4.0)
mesh.refine(criterium)

mesh.save("mesh_t1.vtk")
