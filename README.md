# ReproSim
_Reproducible Simulation library._

**NOTE**: in development, currently just POC (`python3 reprosim/lib.py`).

Planned features:
- Consistent scheduling and random number generation, multiprocess execution.
- Uses async functions to avoid callback hell and [curio](https://github.com/dabeaz/curio)-like trap/syscall model
- Virtual clock jumps forward in time to the next event
- Special state properties allow for various kinds of interpolation between states and make actors functionally immutable inside one scheduling interval