#!/bin/bash
rm devices.csv
threads=8

for c in conf_0 conf_1 conf_2 conf_3;
do
        echo Running with $c
        spark-submit --master local[$threads] experiment/runner.py --threads $threads --output devices.csv --conf experiment.devices.$c
done
