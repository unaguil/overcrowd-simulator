#!/bin/bash

experiment/devices/run_threads.sh
experiment/merge_data devices

experiment/cells/run_threads.sh
experiment/merge_data cells

experiment/internal/run_threads.sh
experiment/merge_data internal
