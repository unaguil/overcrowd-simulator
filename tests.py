import unittest
from device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint

class TestDeviceGenerator(unittest.TestCase):

  def test_generation(self):
     model = RandomWaypoint(200, dimensions=(100, 100), velocity=(0.1, 1.0), wt_max=1.0)

     devices_gen = devices_generator(model, accuracy=(20.0, 30.0))

     for i in range(10):
         devices = next(devices_gen)
         self.assertEqual(200, len(devices))
         device = devices.values()[0]

         self.assertTrue(0 <= device.position[0] <= 100)
         self.assertTrue(0 <= device.position[1] <= 100)

         self.assertTrue(20.0 <= device.accuracy <= 30.0)

if __name__ == '__main__':
    unittest.main()
