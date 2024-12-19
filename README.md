# Adaptive Mesh Refinement (AMR)

![Before AMR](https://i.imgur.com/tgimeyW.png) ![After AMR](https://i.imgur.com/TPWP5l0.png)

## Overview
This project deals with the implementation of an Adaptive Mesh Refinement (AMR) method for the numerical solution of problems. AMR is a numerical technique that adjusts the mesh resolution based on local problem characteristics to optimize computational resources and obtain accurate solutions.

The main goal of the project is to develop such an algorithm, designed to generate Octree (3D) or Quadtree (2D) mesh based on a time-varying physical field and a specified indicator. The algorithm will dynamically refine or coarsen the mesh by analyzing changes in the physical field.

The algorithm is then applied to solve a continuous heat transfer problem, in two dimensions and observe the behavior of the mesh as the solution evolves over time. The results are validated by comparing them with a reference solution obtained using a uniform mesh.

*Please see the [Running the project]() section below for running instructions.*

## Author & Acknowledgments
- Author: [Osmani Dion](mailto:dion.osmani@students.hevs.ch), HES-SO Valais-Wallis Student, Informatique et systèmes de communication
- Supervisor: [Desmons Florian](mailto:florian.desmons@hevs.ch), HES-SO Valais-Wallis Lecturer, Informatique et systèmes de communication

## Table of Contents
1. Installation
2. Getting Started
3. Project Structure
4. Technical Documentation
5. Examples & Usage
6. Results
7. Contributing
8. License

## Installation
- Prerequisites and dependencies
- Step-by-step installation guide
- Environment setup

## Getting Started
- Quick start guide
- Basic usage examples
- Configuration instructions

## Project Structure
```
project/
├── src/
├── tests/
├── examples/
├── docs/
└── ...
```

## Technical Documentation
### Algorithm Description
- Detailed explanation of the AMR algorithm
- Mathematical foundation
- Implementation specifics

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

## Contributing
- How to contribute
- Coding standards
- Testing guidelines

## License
- License information

## References
- Citations
- Related work
- Additional resources
```

Key aspects to emphasize:

1. **Code Documentation**:
   - Document all major functions with docstrings
   - Explain input/output parameters
   - Include code examples
   - Document any assumptions or limitations

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

5. **Maintenance**:
   - How to report issues
   - Update procedures
   - Future development plans
   - Contact information
