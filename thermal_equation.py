from src.mesh import Mesh
from src.node import Node
from src.refinement import CustomRefinementCriterium

# This script implements the
# thermal equation and makes
# use of an adaptive mesh
# refinement

# define physics-related
# constants and parameters
# of the model

# spatial
N: int = 128  # number of cells per dimension
LX: float = 10.0  # length of the domain in x [m]
LY: float = 10.0  # length of the domain in y [m]

# temporal
T: float = 10.0  # total simulation time [s]
DT: float = 0.01  # time step [s]
N_STEPS: int = int(T / DT)  # number of time steps
time: float = 0.0  # current simulation time

# material
RHO: float = 1.204  # density [kg/m^3]
CP: float = 1004.0  # specific heat capacity [J/kg/K]
LAMBDA: float = 0.026  # thermal conductivity [W/m/K]


# create uniform mesh
mesh = Mesh.uniform(n=N, lx=LX, ly=LY, leaf_value=0.0)


# inject values into tree
# to represent source of heat
def heat_source(node: Node) -> None:
    # get node's absolute position
    x, y, _ = node.absolute_origin

    # calculate distance from
    # center of domain
    # (LX/2, LY/2) is the center point
    dx = LX * (x - 0.5)
    dy = LY * (y - 0.5)
    radius = (dx**2 + dy**2) ** 0.5

    # if point is within circle
    # of radius of 2.0 [m]
    if radius <= 2.0:
        node.value = 5.0


mesh.inject(heat_source)

# save initialized mesh
mesh.save("mesh_t0.vtk")

# create refinement criterium
# attention, shall implement better criterium
# that takes into account the difference
# in level with neighboring nodes
criterium = CustomRefinementCriterium(lambda node: node.value > 4.0)
mesh.refine(criterium)

# iterate over time
# for step in range(1,N_STEPS):
for step in range(1, 51):
    # simulation time increases
    time += DT

    # solve the thermal equation
    ...

    # refine and save mesh
    # every 50 steps
    if step % 50 == 0:
        print(f"Step {step} / {N_STEPS}, current simulation time: {time:.3}s")

        # apply refinement criterium
        # mesh.refine(criterium)

        # solve the thermal equation
        mesh.solve(solver)

        # save mesh state
        # mesh.save(f"mesh_t{step}.vtk")

    # continuous energy injection
    # into the domain
    mesh.inject(heat_source)
