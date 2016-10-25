#!/bin/bash
file_name=$1

cat $file_name\_t1.csv > $file_name.csv
cat $file_name\_t2.csv | sed 1d >> $file_name.csv
cat $file_name\_t4.csv | sed 1d >> $file_name.csv
cat $file_name\_t8.csv | sed 1d >> $file_name.csv
cat $file_name\_t16.csv | sed 1d >> $file_name.csv
