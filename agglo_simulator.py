from device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager import GridManager

################################################################################
### Simulation configuration
N_DEVICES = 100
DIMENSIONS = (500, 500)
VELOCITY = (0.1, 1.4)
MAX_PAUSE_TIME = 600.0  # 10 minutes
DENSITY_THRESHOLD = 0.8
N_CELLS = (32, 32)
################################################################################


if __name__ == '__main__':
    model = RandomWaypoint(nr_nodes=N_DEVICES, dimensions=DIMENSIONS,
        velocity=VELOCITY, wt_max=MAX_PAUSE_TIME)

    devices_gen = devices_generator(model)

    print("Agglomeration simulator v0.1")
    print("============================")

    grid_manager = GridManager(dimensions=DIMENSIONS, n_cells=N_CELLS)

    print("Avg. density %.5f devices/m^2" % (N_DEVICES / grid_manager.area))
    print("Cell area: %.3f m^2" % grid_manager.cell_area)

    first_time = True
    while True:
        devices = next(devices_gen)
        grid_manager.update(devices.values())
