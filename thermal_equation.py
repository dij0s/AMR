import sys

from src.benchmark import Benchmark
from src.mesh import Mesh
from src.node import Node
from src.refinement import (
    LogScaleGradientRefinuementCriterium,
)
from src.scheme import SecondOrderCenteredFiniteDifferences

# this script implements the
# thermal equation and makes
# use of an adaptive mesh
# refinement
# the domain ensures energy
# conservation as a continuous
# heat source is injected into
# the domain

# benchmark the simulation
# to measure performance
# individual functions
# are decorated for benchmarking
# inside the Mesh class
benchmark = Benchmark()


# wrap the simulation
# in a function to enable
# enhanced benchmarking
@benchmark.repeat
def simulation():
    # define physics-related
    # constants and parameters
    # of the model

    # adaptive mesh refinement
    MIN_RELATIVE_DEPTH: int = (
        -3
    )  # minimum depth of the tree (relative to the base cell)
    MAX_RELATIVE_DEPTH: int = 2  # maximum depth of the tree (relative to the base cell)

    # spatial
    N: int = 64  # number of cells per dimension
    LX: float = 10.0  # length of the domain in x [m]
    LY: float = 10.0  # length of the domain in y [m]
    DX: float = LX / (
        N / 2**MAX_RELATIVE_DEPTH
    )  # spatial step in x (smallest cell) [m]
    DY: float = LY / (
        N / 2**MAX_RELATIVE_DEPTH
    )  # spatial step in y (smallest cell) [m]

    # temporal
    # T: float = 2.0  # total simulation time [s]
    # DT: float = 0.0002  # time step [s]
    T: float = 100.0  # total simulation time [s]
    DT: float = 0.01  # time step [s]
    N_STEPS: int = int(T / DT)  # number of time steps
    simulation_time: float = 0.0  # current simulation time

    N_RECORDS: int = 200  # number of records to save
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
    #     print(f"DT: {DT}s ≮ {((RHO / (LAMBDA * CP * DX**2)) * 0.3):.4}s")
    #     raise ValueError(
    #         "Stability condition not met! Please provide a smaller time step."
    #     )

    # create uniform mesh
    mesh, current_absolute_depth = Mesh.uniform(
        n=N, lx=LX, ly=LY, leaf_value=lambda: 5.0
    )
    # compute absolute minimal
    # and maximal depth of
    # the tree
    min_absolute_depth: int = current_absolute_depth + MIN_RELATIVE_DEPTH
    max_absolute_depth: int = current_absolute_depth + MAX_RELATIVE_DEPTH

    # inject values into tree
    # to represent source of heat
    def heat_source(node: Node) -> None:
        # get node's absolute
        # centered origin
        x, y, _ = node.absolute_centered_origin

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
        laplacian_factor=LAPLACIAN_FACTOR, d1=DX, d2=DY
    )

    # create refinement criterium
    # based on the gradient change
    log_criterium = LogScaleGradientRefinuementCriterium(threshold=0.1)

    # reset benchmark
    # after simulation
    # setup
    benchmark.reset()

    # iterate over time
    for step in range(1, N_STEPS + 1):
        # simulation time increases
        simulation_time += DT

        # continuous energy injection
        # into the domain
        mesh.inject(heat_source)

        # solve the thermal equation
        mesh.solve(solver)

        # refine and save mesh
        # every n steps
        if step % record_interval == 0:
            print(
                f"Step {step} / {N_STEPS}, current simulation time: {simulation_time:.3}s"
            )

            # refine mesh based
            # on constraints
            mesh.refine(
                log_criterium,
                min_depth=min_absolute_depth,
                max_depth=max_absolute_depth,
            )

            # save mesh state
            mesh.save(f"mesh_t{step:05}.vtk")

    # get total elapsed time
    print(f"Total elapsed time: {int(benchmark.elapsed)}s")

    # display benchmark results
    benchmark.display()


if __name__ == "__main__":
    try:
        # get number of iterations from
        # command line, default to 1 if
        # not provided
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        # run the simulation
        simulation(n=n)
    except ValueError:
        print("Usage: python thermal_equation.py [number of iterations]")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
