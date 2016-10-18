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

def save_data(data, file_name):
    headers = [
        'devices', 'dimensions', 'velocity',
        'accuracy', 'max_pause_time', 'cells',
        'sim_total_time', 'threads', 'avg_matrix_comp_time'
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
    iterations = 0

    while sim_time < data['sim_total_time']:
        devices = next(devices_gen)

        print 'Computing matrix for iteration %d' % iterations

        start_time = time.time()
        g_manager.update(devices.values())
        elapsed_time = time.time() - start_time

        elapsed_time_sum += elapsed_time
        iterations += 1

        print 'Density matrix computed in %.2f s' % elapsed_time

        sim_time += elapsed_time
        print 'Current simulation time: %.2f s' % sim_time

    sc.stop()

    avg_time = elapsed_time_sum / float(iterations)

    print 'Simulation finished'
    print '==================='
    print 'Iterations: %d' % iterations
    print 'Avg. matrix computation time: %.2f' % avg_time

    data['avg_matrix_comp_time'] = avg_time

    save_data(data, file_name)
