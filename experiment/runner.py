from grid_manager.device_gen import devices_generator
from pymobility.models.mobility import RandomWaypoint
from grid_manager.grid_manager import GridManager

from pyspark import SparkContext
from pyspark import SparkConf

from experiment.basic_conf import configuration as c

import time

if __name__ == '__main__':
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

        print 'Density matrix computed in %.2f seconds' % elapsed_time

        density_matrix = g_manager.density_matrix
        print density_matrix

        print 'Waiting %.2f s until next update' % c['update_interval']
        time.sleep(c['update_interval'])

        sim_time += c['update_interval']

    sc.stop()

    avg_time = elapsed_time_sum / float(iterations)

    print 'Simulation finished'
    print '==================='
    print 'Iterations: %d' % iterations
    print 'Avg. matrix computation time: %.2f' % avg_time
