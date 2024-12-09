from random import gauss

from src.mesh import Mesh
from src.refinement import CustomRefinementCriterium

# create uniform mesh
# with random values
# in a normal distribution
mesh = Mesh.uniform(
    n=16,
    leaf_value=lambda: gauss(mu=0.0, sigma=1.0) + 2.5,
    lx=10,
    ly=10,
    lz=10,
)

mesh.save("mesh_t0.vtk")

# refine mesh based
# on custom criterium
criterium = CustomRefinementCriterium(lambda node: node.value > 4.0)
mesh.refine(criterium)

mesh.save("mesh_t1.vtk")
