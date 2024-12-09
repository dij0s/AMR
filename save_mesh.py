from random import random

from src.mesh import Mesh
from src.refinement import CustomRefinementCriterium

# create uniform mesh
# with random values
# between 0 and 5
mesh = Mesh(lx=10, ly=10)
root = mesh.uniform(n=16, leaf_value=lambda: random() * 5.0)

mesh.save("mesh_t0.vtk")

# refine mesh
criterium = CustomRefinementCriterium(lambda node: node.value > 4.0)
mesh.refine(criterium)

mesh.save("mesh_t1.vtk")
