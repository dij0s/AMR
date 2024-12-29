# Adaptive Mesh Refinement (AMR)

![](#gh-light-mode-only)
![AMR on heat transfer simulation](#gh-dark-mode-only)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://i.imgur.com/LhYwpfS.png">
  <source media="(prefers-color-scheme: light)" srcset="https://i.imgur.com/Q8LpTT0.png">
  <img alt="AMR on heat diffusion simulation" src="https://i.imgur.com/LhYwpfS.png">
</picture>

## Overview
This project deals with the implementation of an Adaptive Mesh Refinement (AMR) method for the numerical solution of problems.
AMR is a numerical technique that adjusts the mesh resolution based on local problem characteristics to optimize computational resources and obtain accurate solutions.

The main goal of the project is to develop such an algorithm, designed to generate Octree (3D) or Quadtree (2D) mesh based on a time-varying physical field and a specified indicator.
The algorithm will dynamically refine or coarsen the mesh by analyzing changes in the physical field.

The algorithm is then applied to solve a continuous heat transfer problem, in two dimensions, and observe the behavior of the mesh as the solution evolves over time.
The results are validated by comparing them with a reference solution obtained using a uniform mesh.

The following sections provide a detailed overview of the project.

*Please see the [Running the project](#running-the-project) section below for running instructions.*

## Author & Acknowledgments
[@Osmani Dion](mailto:dion.osmani@students.hevs.ch), Author, HES-SO Valais-Wallis Student, Informatique et systèmes de communication (3rd year)

[@Desmons Florian](mailto:florian.desmons@hevs.ch), Supervisor, HES-SO Valais-Wallis Lecturer, Informatique et systèmes de communication

## Technical Documentation

The following sections provide a detailed technical overview of the project, including the algorithm description, code architecture and performance considerations.

### Algorithm Description

The overall *simulation algorithm* can be broken down into the following steps:

1. Initialization:
   - Create the initial mesh based on the domain size and resolution.
   - Assign initial values to the mesh cells based on the initial temperature field.

2. Time Integration:
   - Iterate over time steps until the final time is reached.

3. Solve the Heat Equation:
    - Compute the heat diffusion equation using finite differences.
    - Update the temperature field based on the computed values.

4. Adaptive Mesh Refinement:
    - Evaluate the refinement criterium based on the temperature field.
    - Refine or coarsen the mesh based on the previous criterium.

5. Data Export:
    - Save the simulation data for visualization.

The *heat equation solver* is based on the finite difference method, which discretizes the heat equation in space and time.

### Code Architecture
- Core components and their interactions
- Class hierarchy
- Key data structures
- Important functions/methods

### Performance
- Complexity analysis
- Benchmarks
- Optimization techniques used

## Examples & Usage
- Detailed code examples
- Common use cases
- Parameter configurations
- Best practices

## Results
- Validation results
- Performance metrics
- Visualization of example outputs
- Comparison with other methods (if applicable)

## Running the project
The project has been developed in Python using [uv](https://astral.sh/blog/uv), an extremely fast Python package installer and resolver, written in Rust, and designed as a drop-in-replacement for pip and pip-tools workflows.

I recommend using `uv` to run the project as it allows for a fully reproducible environment. To install `uv`, follow the instructions on the [official website](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

After installing `uv`, you can simply run the project using the following command, at the root of the project directory:

```bash
uv run thermal_equation.py
```

This will execute the main script of the project used to solve the heat transfer problem.

One can also provide an extra argument to the script to specify the number of iterations to run:

```bash
uv run thermal_equation.py 10 # Run for 10 iterations
```

It provides an easy way to run a simulation multiple times which can be useful for testing and validation purposes.

### Modifying the simulation

If you are willing to modify the physical field, the physical properties or the refinement criterium, you can do so by editing the `thermal_equation.py` script.
Here is an example of the physical properties and mesh/simulation parameters that can be modified:

```python
# adaptive mesh refinement
MIN_RELATIVE_DEPTH: int = -3  # minimum depth of the tree (relative to the base cell)
MAX_RELATIVE_DEPTH: int = 2  # maximum depth of the tree (relative to the base cell)

# spatial
N: int = 64  # number of cells per dimension
LX: float = 10.0  # length of the domain in x [m]
LY: float = 10.0  # length of the domain in y [m]

# temporal
T: float = 100.0  # total simulation time [s]
DT: float = 0.01  # time step [s]

N_RECORDS: int = 200  # number of records to save

# material
RHO: float = 0.06  # density [kg/m^3]
CP: float = 204.0  # specific heat capacity [J/kg/K]
LAMBDA: float = 1.026  # thermal conductivity [W/m/K]
```

### Running the benchmark
A preset of lineout Curve2D VisIt export folders are available in the `export/` directory. You can run the tests using the following command:

```bash
uv run compare_lineouts.py <reference_folder/path> <comparison_folder/path>
```

The order in which the folders are specified matters as the first folder is assumed to be the reference simulation data against which we compare another simulation's data.

## License
- License information

## References
- Citations
- Related work
- Additional resources
```

Key aspects to emphasize:

2. **Technical Details**:
   - Algorithm implementation details
   - Data structures used
   - Performance considerations
   - Error handling

3. **Usage Guidelines**:
   - Clear installation instructions
   - Step-by-step usage examples
   - Common pitfalls and solutions
   - Configuration options

4. **Results and Validation**:
   - Test cases and their results
   - Performance benchmarks
   - Visual examples
   - Validation methodology
