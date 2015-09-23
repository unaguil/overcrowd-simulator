from device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint

################################################################################
### Simulation configuration
W = 500
H = 500
################################################################################


if __name__ == '__main__':
    model = RandomWaypoint(200, dimensions=(100, 100), velocity=(0.1, 1.0), wt_max=1.0)
    devices_gen = devices_generator(model)

    while True:
        devices = next(devices_gen)
        device = devices.values()[0]
        print device.id
        print device.position
        print device.accuracy
