""" Test the FDTD detectors """

# To run tests in a conda env, use python -m pytest in the root
# to specify a test,  -k "test_current_detector"
# To view output, -rA
# to run with all backends, --all_backends.
# with --all_backends, --maxfail=1 is recommended to avoid blowing up the scrollback!

## Imports
import fdtd
from fdtd.backend import backend as bd
from fdtd.waveforms import normalized_gaussian_pulse
from fdtd.conversions import *

import pytest
from fixtures import grid, pml, periodic_boundary, backend_parametrizer
import matplotlib.pyplot as plt

from fdtd.grid import d_
## Tests

x_ = 4
y_ = 4
z_ = 4

#theory-driven development? there must be a more efficient way to test this kind of code...

pytest_generate_tests = backend_parametrizer # perform tests over all backends


def test_object_grid_overlap(grid, pml):
    grid[x_-1:x_+1,y_-1:y_+1,z_-1:z_+1] = fdtd.AbsorbingObject(permittivity=1.0,
    conductivity=conductivity)
    # grid[x_,y_,z_] = fdtd.PointSource(period=500)



# @pytest.mark.skipif(skip_test_backend, reason="PyTorch is not installed.")
def test_current_detector_all_bends(grid, pml, backends):
    fdtd.set_backend(backends)

    # we want our test cases to be orthogonal:
    # The test case with the patch antenna also relies on
    # the electric field detector & PEC, seems like a smaller test could be in order

    #However, because of the overlapping object issue, seems like this'll be harder.

    conductivity = 100
    # absorb = bd.ones((grid.Nx,grid.Ny,grid.Nz))
    # absorb[x_,y_,z_] = 0
    grid[x_-1:x_+1,y_-1:y_+1,z_-1:z_+1] = fdtd.AbsorbingObject(permittivity=100.0,
    conductivity=conductivity)

    #AbsorbingObject doesn't create a magnetic field?
    #How could that ever cause a current density?

    # grid[x_,y_,z_] = fdtd.PointSource(period=500)
    cd = fdtd.CurrentDetector(name="Dave")
    grid[x_,y_,z_] = cd
    grid[x_:x_,y_:y_,z_:z_] = fdtd.BlockDetector()
    # FIXME: AbsorbingObject must be added last for some reason,


    n = 1000
    # grid.run(total_time=n)
    for _ in range(n):
        grid.update_E()
        grid.E[x_,y_,z_, d_.Z] = normalized_gaussian_pulse(grid.time_passed,100*grid.time_step,
                                                        center=500*grid.time_step)
        grid.update_H()
        grid.time_steps_passed += 1

    #
    current_time_history = bd.array(grid.detectors[0].I).reshape(n)
    electric_field_time_history = bd.array(grid.detectors[1].E).reshape(n,3)[:,d_.Z]
    print(grid.E[x_,y_,z_,d_.Z])

    print(current_time_history)
    voltage = electric_field_time_history*grid.grid_spacing
    resistivity = 1.0/conductivity
    resistance = (resistivity * grid.grid_spacing) / (grid.grid_spacing*grid.grid_spacing)
    expected_current = voltage / resistance
    # print(expected_current)
    # print(current_time_history)
    # plt.plot(current_time_history)
    # plt.show()
    # plt.plot(electric_field_time_history)
