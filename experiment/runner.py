from grid_manager.device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager.grid_manager import GridManager

from pyspark import SparkContext
from pyspark import SparkConf

from experiment.basic_conf import configuration as c

import time
import csv
import os.path
import sys

def save_data(data, file_name):
    headers = [
        'devices', 'dimensions', 'velocity',
        'accuracy', 'max_pause_time', 'cells',
        'sim_total_time', 'avg_matrix_comp_time'
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
    if len(sys.argv) < 2:
        print 'Output file required'
        sys.exit()

    print 'Starting simulation'
    print 'Total time: %d' % c['sim_total_time']

    model = RandomWaypoint(nr_nodes=c['devices'], dimensions=c['dimensions'],
        velocity=c['velocity'], wt_max=c['max_pause_time'])

    devices_gen = devices_generator(model, accuracy=c['accuracy'])

    conf = SparkConf().setAppName('GridManagerExperiment')
    sc = SparkContext(conf=conf)

    g_manager = GridManager(spark_context=sc, dimensions=c['dimensions'], n_cells=c['cells'])

    sim_time = 0

    elapsed_time_sum = 0
    iterations = 0

    while sim_time < c['sim_total_time']:
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

    data = c
    data['avg_matrix_comp_time'] = avg_time

    save_data(data, sys.argv[1])
