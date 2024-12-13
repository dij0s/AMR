import time

from src.mesh import Mesh
from src.node import Node
from src.refinement import GradientRefinementCriterium
from src.scheme import SecondOrderCenteredFiniteDifferences

# this script implements the
# thermal equation and makes
# use of an adaptive mesh
# refinement
# the domain ensures energy
# conservation as a continuous
# heat source is injected into
# the domain

# define physics-related
# constants and parameters
# of the model

# adaptive mesh refinement
MAX_RELATIVE_DEPTH: int = 2  # maximum depth of the tree (relative to the base cell)

# spatial
N: int = 64  # number of cells per dimension
LX: float = 10.0  # length of the domain in x [m]
LY: float = 10.0  # length of the domain in y [m]
DX: float = LX / (N / 2**MAX_RELATIVE_DEPTH)  # spatial step in x (smallest cell) [m]
DY: float = LY / (N / 2**MAX_RELATIVE_DEPTH)  # spatial step in y (smallest cell) [m]

# temporal
T: float = 100.0  # total simulation time [s]
DT: float = 0.01  # time step [s]
N_STEPS: int = int(T / DT)  # number of time steps
simulation_time: float = 0.0  # current simulation time

N_RECORDS: int = 20  # number of records to save
record_interval: int = N_STEPS // N_RECORDS  # interval between records

# material
# RHO: float = 1.204  # density [kg/m^3]
# CP: float = 1004.0  # specific heat capacity [J/kg/K]
# LAMBDA: float = 0.026  # thermal conductivity [W/m/K]
RHO: float = 0.06  # density [kg/m^3]
CP: float = 204.0  # specific heat capacity [J/kg/K]
LAMBDA: float = 1.026  # thermal conductivity [W/m/K]

LAPLACIAN_FACTOR: float = DT * LAMBDA / RHO / CP  # Laplacian factor

# check stability condition
# if not DT < (RHO / (LAMBDA * CP * DX**2)) * 0.3:
#     print(f"{DT} ≮ {((RHO / (LAMBDA * CP * DX**2)) * 0.3):.4}")
#     raise ValueError("Stability condition not met! Please provide a smaller time step.")

# create uniform mesh
mesh, current_absolute_depth = Mesh.uniform(n=N, lx=LX, ly=LY, leaf_value=lambda: 5.0)
# compute absolute maximal
# depth of the tree
max_absolute_depth: int = current_absolute_depth + MAX_RELATIVE_DEPTH


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
        node.value = 60.0  # [°C]


mesh.inject(heat_source)

# save initialized mesh
mesh.save("mesh_t00000.vtk")

# create solving scheme
solver = SecondOrderCenteredFiniteDifferences(
    laplacian_factor=LAPLACIAN_FACTOR, d1=DX, d2=DY, LX=LX, LY=LY, DX=DX, DY=DY
)

# create refinement criterium
# based on the gradient change
criterium = GradientRefinementCriterium(threshold=0.8)

# benchmark the time
start = time.time()

# iterate over time
for step in range(1, N_STEPS):
    # simulation time increases
    simulation_time += DT

    # solve the thermal equation
    mesh.solve(solver)

    # refine and save mesh
    # every n steps
    if step % record_interval == 0:
        print(
            f"Step {step} / {N_STEPS}, current simulation time: {simulation_time:.3}s"
        )

        # apply refinement criterium
        mesh.refine(criterium, max_depth=max_absolute_depth)

        # save mesh state
        mesh.save(f"mesh_t{step:04}.vtk")

    # continuous energy injection
    # into the domain
    mesh.inject(heat_source)

# benchmark the time
elapsed = time.time() - start
print(f"Elapsed time: {int(elapsed)}s")
