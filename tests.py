import unittest
from device_gen import devices_generator
from grid_manager import GridManager
from pymobility.models.mobility import RandomWaypoint

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

        self.assertEquals(100, grid_manager.rows)
        self.assertEquals(100, grid_manager.columns)

        for i in range(grid_manager.rows):
            for j in range(grid_manager.columns):
                self.assertEquals(0.0, grid_manager[i, j].density)

if __name__ == '__main__':
    unittest.main()
