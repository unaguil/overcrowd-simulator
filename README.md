# agglo-simulator

[![Build Status](https://travis-ci.com/unaguil/agglo-simulator.svg?token=fJZNuvpQu2CHYrmKy2jB&branch=spark)](https://travis-ci.com/unaguil/agglo-simulator)

Requirements
============

* Tested with

  * Python 2.7
  * Spark 2.0.1 (http://spark.apache.org/)

* Install APT required dependencies

        apt-get install libgeos-dev libspatialindex-dev

* Install Python requirements

        pip install -r requirements.txt

Testing
=======

Configure enviroment variables to point to your Spark installation directory

    export SPARK_HOME=/opt/spark-2.0.1-bin-hadoop2.7
    export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.3-src.zip:$PYTHONPATH

Run tests with

    nosetests -s


Launching sample application
============================

Launch the sample Python application locally with

    spark-submit --master local agglo_simulator.py


Launch all experiments (locally)
================================

Change to the main directory and run the following script

    experiment/run_all.sh

The output of each experiment is written to a different CSV file in the local
directory.
