#!/bin/bash
rm threads.csv

for i in 1 2 4 8;
do
        echo Running with $i threads
        spark-submit --master local[$i] experiment/runner.py $i threads.csv
done
