from device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager import GridManager
import pygame
from pygame.locals import *
import numpy

################################################################################
### Simulation configuration
N_DEVICES = 1
DIMENSIONS = (100, 100)
VELOCITY = (0.1, 1.4)
MAX_PAUSE_TIME = 10.0  # 10 seconds
N_CELLS = (64, 64)
DENSITY_SCALE = (0.0, 0.2)
################################################################################

SCREEN_SIZE = (518, 518)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def scale_color(density, density_scale):
    scale = density_scale[1] - density_scale[0]
    red_value = int(255 * density / float(scale))
    if red_value > 255:
        red_value = 255

    return (red_value, 0, 0)

if __name__ == '__main__':
    model = RandomWaypoint(nr_nodes=N_DEVICES, dimensions=DIMENSIONS,
        velocity=VELOCITY, wt_max=MAX_PAUSE_TIME)

    devices_gen = devices_generator(model, accuracy=(0.0, 3.0))

    print("Agglomeration simulator v0.1")
    print("============================")

    grid_manager = GridManager(dimensions=DIMENSIONS, n_cells=N_CELLS)

    print("Avg. density %.5f devices/m^2" % (N_DEVICES / grid_manager.area))
    print("Cell area: %.3f m^2" % grid_manager.cell_area)

    screen = pygame.display.set_mode(SCREEN_SIZE)
    screen.fill(BLACK)
    pygame.display.flip()

    surface = pygame.Surface(N_CELLS)

    exit = False
    while not exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True

        devices = next(devices_gen)
        grid_manager.update(devices.values())

        screen.fill(WHITE)

        density_matrix = grid_manager.density_matrix
        for i in range(density_matrix.shape[0]):
            for j in range(density_matrix.shape[1]):
                color = scale_color(density_matrix[i, j], DENSITY_SCALE)
                surface.set_at((i, j), color)

        pygame.transform.scale(surface, SCREEN_SIZE, screen)

        pygame.display.flip()
