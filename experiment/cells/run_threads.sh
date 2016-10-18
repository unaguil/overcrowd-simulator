#!/bin/bash
for t in 1 2 4 8 16;
do
        experiment/cells/run.sh $t
done
