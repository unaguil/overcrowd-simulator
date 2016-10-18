#!/bin/bash
for t in 1 2 4 8 16;
do
        experiment/devices/run.sh $t
done
