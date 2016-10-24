from grid_manager.device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager.grid_manager import GridManager

from pyspark import SparkContext
from pyspark import SparkConf

import time
import csv
import os.path
import sys
import argparse
import importlib
import numpy

def save_data(data, file_name):
    headers = [
        'devices', 'dimensions', 'velocity',
        'accuracy', 'max_pause_time', 'cells', 'iterations',
        'sim_total_time', 'threads', 'avg_matrix_comp_time', 'total_data_size',
        'mean_matrix_comp_time', 'std_matrix_comp_time'
    ]

    file_exists = os.path.isfile(file_name)
    if file_exists:
        open_mode = 'a'
    else:
        open_mode = 'w'

    with open(file_name, open_mode) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

def get_size(device):
    return sys.getsizeof(device.id) + device.position.nbytes + sys.getsizeof(device.accuracy)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", help="number of threads used in this experiment")
    parser.add_argument("--output", help="file to append the experiment data")
    parser.add_argument("--conf", help="configuration used for this experiment")

    args = parser.parse_args()

    if args.conf:
        module = importlib.import_module(args.conf)
        data = module.configuration
    else:
        from experiment.basic_conf import configuration as data

    if args.threads:
        data['threads'] = args.threads
    else:
        data['threads'] = 'Unknown'

    if args.output:
        file_name = args.output
    else:
        file_name = 'default_output.csv'

    print 'Starting simulation'
    print data

    model = RandomWaypoint(nr_nodes=data['devices'], dimensions=data['dimensions'],
        velocity=data['velocity'], wt_max=data['max_pause_time'])

    devices_gen = devices_generator(model, accuracy=data['accuracy'])

    conf = SparkConf().setAppName('GridManagerExperiment')
    sc = SparkContext(conf=conf)

    g_manager = GridManager(spark_context=sc, dimensions=data['dimensions'], n_cells=data['cells'])

    sim_time = 0

    elapsed_time_sum = 0
    iteration = 0

    device_size = None
    total_data_size = 0

    values = []

    while iteration < data['iterations']:
        devices = next(devices_gen)

        if device_size is None:
            device_size = get_size(devices.values()[0])

        total_data_size += device_size * len(devices)

        print 'Computing matrix for iteration %d/%d' % (iteration, data['iterations'])

        start_time = time.time()
        g_manager.update(devices.values())
        elapsed_time = time.time() - start_time

        values.append(elapsed_time)

        elapsed_time_sum += elapsed_time
        iteration += 1

        print 'Density matrix computed in %.2f s' % elapsed_time

        density_matrix = g_manager.density_matrix
        print density_matrix

        sim_time += elapsed_time
        print 'Current simulation time: %.2f s' % sim_time

    sc.stop()

    avg_time = elapsed_time_sum / float(data['iterations'])

    print 'Simulation finished'
    print '==================='
    print 'Iterations: %d' % data['iterations']
    print 'Avg. matrix computation time (seconds): %.2f' % avg_time
    print 'Total data size (bytes): %d' % total_data_size

    data['avg_matrix_comp_time'] = avg_time
    data['sim_total_time'] = elapsed_time_sum
    data['total_data_size'] = total_data_size
    data['mean_matrix_comp_time'] = numpy.mean(values)
    data['std_matrix_comp_time'] = numpy.std(values)

    save_data(data, file_name)
