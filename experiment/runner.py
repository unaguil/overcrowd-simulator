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

    while sim_time < c['sim_total_time']:
        devices = next(devices_gen)
        g_manager.update(devices.values())
        density_matrix = g_manager.density_matrix
        print density_matrix

        print 'Waiting %.2f s until next update' % c['update_interval']
        time.sleep(c['update_interval'])

        sim_time += c['update_interval']

    sc.stop()

    print 'Simulation finished'
