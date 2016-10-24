#!/bin/bash
for t in 1 2 4 8 16;
do
        experiment/internal/run.sh $t
done
