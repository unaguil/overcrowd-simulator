from grid_manager.device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager.grid_manager import GridManager
import argparse

from pyspark import SparkContext
from pyspark import SparkConf

################################################################################
### Simulation configuration
N_DEVICES = 20
DIMENSIONS = (100, 100)
VELOCITY = (0.1, 1.4)
ACCURACY = (0.0, 3.0)
MAX_PAUSE_TIME = 10.0  # 10 seconds
N_CELLS = (6, 6)
DENSITY_SCALE = (0.0, 0.2)
################################################################################
SCREEN_SIZE = (518, 518)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
################################################################################

def scale_color(density, density_scale):
    scale = density_scale[1] - density_scale[0]
    red_value = int(255 * density / float(scale))
    if red_value > 255:
        red_value = 255

    return (red_value, 0, 0)

if __name__ == '__main__':
    description = 'Agglomeration simulator v0.1'

    model = RandomWaypoint(nr_nodes=N_DEVICES, dimensions=DIMENSIONS,
        velocity=VELOCITY, wt_max=MAX_PAUSE_TIME)

    devices_gen = devices_generator(model, accuracy=ACCURACY)

    print(description)
    print("============================")

    conf = SparkConf().setAppName('GridManager')
    sc = SparkContext(conf=conf)

    g_manager = GridManager(spark_context=sc, dimensions=DIMENSIONS, n_cells=N_CELLS)

    print("Avg. density %.5f devices/m^2" % (N_DEVICES / g_manager.area))
    print("Cell area: %.3f m^2" % g_manager.cell_area)

    exit = False
    while not exit:
        devices = next(devices_gen)
        g_manager.update(devices.values())

        # screen.fill(WHITE)

        density_matrix = g_manager.density_matrix
        print density_matrix

    sc.stop()
