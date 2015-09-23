import random

class Device:

    def __init__(self, id):
        self.id = id
        self.position = None
        self.accuracy = None

class DeviceGenerator:

    def __init__(self, mobility_model, accuracy_range=(0.0, 50.0)):
        self.devices = {}
        self.model_iter = iter(mobility_model)
        self.accuracy_range = accuracy_range

        for n in range(mobility_model.nr_nodes):
            node_id = str(n)
            self.devices[node_id] = Device(node_id)

    def __iter__(self):
        while True:
            positions = next(self.model_iter)
            for index, node_id in enumerate(sorted(self.devices.keys())):
                self.devices[node_id].position = positions[index]
                accuracy = random.random() * self.accuracy_range[1] + self.accuracy_range[0]
                self.devices[node_id].accuracy = accuracy

            yield self.devices

def devices_generator(*args, **kwargs):
    return iter(DeviceGenerator(*args, **kwargs))
