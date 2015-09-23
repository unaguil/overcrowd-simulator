import unittest
from device_gen import devices_generator, Device
from grid_manager import GridManager
from pymobility.models.mobility import RandomWaypoint
import numpy

class TestDeviceGenerator(unittest.TestCase):

    def test_generation(self):
        model = RandomWaypoint(200, dimensions=(100, 100), velocity=(0.1, 1.0), wt_max=1.0)

        devices_gen = devices_generator(model, accuracy=(20.0, 30.0))

        for i in range(10):
            devices = next(devices_gen)
            self.assertEqual(200, len(devices))

            device_ids = set([])
            for node_id, device in devices.items():
                device_ids.add(node_id)
                self.assertTrue(0 <= device.position[0] <= 100)
                self.assertTrue(0 <= device.position[1] <= 100)

                self.assertTrue(20.0 <= device.accuracy <= 30.0)

            self.assertEquals(200, len(devices.keys()))
            self.assertEquals(200, len(device_ids))

class TestGridManager(unittest.TestCase):

    def test_grid_manager(self):
        grid_manager = GridManager(dimensions=(250, 100), n_cells=(100, 100))

        self.assertEquals((250, 100), grid_manager.dimensions)
        self.assertEquals((100, 100), grid_manager.n_cells)
        self.assertEquals((2.5, 1.0), grid_manager.cell_dimensions)
        self.assertEquals(2.5, grid_manager.cell_area)

        self.assertEquals(100, grid_manager.rows)
        self.assertEquals(100, grid_manager.columns)

        for i in range(grid_manager.rows):
            for j in range(grid_manager.columns):
                self.assertEquals(0.0, grid_manager[i, j].occupation)

                expected_box = (
                    i * grid_manager.cell_dimensions[0],
                    j * grid_manager.cell_dimensions[1],
                    i * grid_manager.cell_dimensions[0] + grid_manager.cell_dimensions[0],
                    j * grid_manager.cell_dimensions[1] + grid_manager.cell_dimensions[1]
                )

                self.assertEquals(expected_box, grid_manager[i, j].box)

    def test_grid(self):
        dimensions_list = [(6, 6), (12, 12), (24, 24), (150, 150), (200, 200)]
        cell_sizes = [(6, 6), (12, 12), (24, 24)]
        for dimensions in dimensions_list:
            for n_cells in cell_sizes:
                grid_manager = GridManager(dimensions=dimensions, n_cells=n_cells)

                devices = [
                    Device("0", (1.0, 1.0), 1.0),
                    Device("1", (3.0, 3.0), 1.0),
                    Device("3", (2.0, 2.0), 1.0),
                    Device("2", (5.0, 5.0), 1.0),
                ]

                grid_manager.update(devices)

                self.assertEquals(n_cells, grid_manager.shape)
                self.assertEquals(n_cells[0], grid_manager.rows)
                self.assertEquals(n_cells[1], grid_manager.columns)
                cell_area = dimensions[0] / float(n_cells[0]) * dimensions[1] / float(n_cells[1])
                self.assertTrue(numpy.isclose(cell_area, grid_manager.cell_area))

                self.assertTrue(numpy.isclose(len(devices), grid_manager.occupation_matrix.sum()))

                expected_avg_density = len(devices) / float(grid_manager.n_cells[0] * grid_manager.n_cells[1])
                self.assertTrue(expected_avg_density, grid_manager.density_matrix.mean())

    def test_wall_close_density(self):
        grid_manager = GridManager(dimensions=(6, 6), n_cells=(6, 6))

        devices = [
            Device("0", (0.0, 0.0), 1.0)
        ]

        grid_manager.update(devices)

        self.assertTrue(numpy.isclose(1.0, grid_manager.occupation_matrix.sum()))

    def test_occupation_matrix(self):
        grid_manager = GridManager(dimensions=(6, 6), n_cells=(6, 6))

        devices = [
            Device("0", (1.0, 1.0), 1.0),
            Device("1", (3.0, 3.0), 1.0),
            Device("2", (2.0, 2.0), 1.0),
            Device("3", (5.0, 5.0), 1.0)
        ]

        grid_manager.update(devices)

        expected_matrix =  numpy.array(
           [[ 0.25,  0.25,  0.  ,  0.  ,  0.  ,  0.  ],
            [ 0.25,  0.5 ,  0.25,  0.  ,  0.  ,  0.  ],
            [ 0.  ,  0.25,  0.5 ,  0.25,  0.  ,  0.  ],
            [ 0.  ,  0.  ,  0.25,  0.25,  0.  ,  0.  ],
            [ 0.  ,  0.  ,  0.  ,  0.  ,  0.25,  0.25],
            [ 0.  ,  0.  ,  0.  ,  0.  ,  0.25,  0.25]]
        )

        self.assertTrue(numpy.allclose(expected_matrix, grid_manager.occupation_matrix))

if __name__ == '__main__':
    unittest.main()
