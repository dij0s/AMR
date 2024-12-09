from src.mesh import Mesh

mesh = Mesh(lx=10, ly=10)
root = mesh.uniform(n=16, leaf_value=5.0)

mesh.save("mesh.vtk")
