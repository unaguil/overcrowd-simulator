#/bin/sh
export SPARK_HOME=/opt/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.9-src.zip:$PYTHONPATH
echo $SPARK_HOME
echo $PYTHONPATH
