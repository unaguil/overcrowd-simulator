
def add_pyspark_path():
    """
    Add PySpark to the PYTHONPATH
    Thanks go to this project: https://github.com/holdenk/sparklingpandas
    """
    import sys
    import os

    try:
        sys.path.append(os.path.join(os.environ['SPARK_HOME'], "python"))
        sys.path.append(os.path.join(os.environ['SPARK_HOME'],
            "python","lib","py4j-0.10.1-src.zip"))
    except KeyError:
        print "SPARK_HOME not set"
        sys.exit(1)

add_pyspark_path()
from pyspark import SparkContext
from pyspark import SparkConf
import unittest

class SparkTestCase(unittest.TestCase):

    def setUp(self):
        conf = SparkConf()
        conf.set("spark.executor.memory","1g")
        conf.set("spark.cores.max", "1")
        #conf.set("spark.master", "spark://10.48.1.21:7077")
        conf.set("spark.app.name", "nosetest")

        self.sc = SparkContext(conf=conf)
        self.sc.setLogLevel("INFO")

    def tearDown(self):
        self.sc.stop()
