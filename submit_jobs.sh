#!/bin/bash

# Anzahl der Durchläufe pro Test
NUM_RUNS=3

# Anzahl der Tests
NUM_TESTS=3

# Manuell festgelegte Parameter
param2=5
param3=15
param5=1000
param6=0.1
param7=0.3
param8=0.1

input_file_name=I.11.19

# Hauptordner für die Tests
test_dir=test_population_size

# erstelle Verzeichnis
mkdir -p $test_dir

# Schleife für Tests
for ((k=1; k<=NUM_TESTS; k++)); do
    param4=$((10 + (k * 20)))

    # erstelle Ordner für jeden Testlauf (run_k)
    test_run_dir=$test_dir/run_$k
    mkdir -p "$test_run_dir"

    # Innere Schleife für Durchläufe
    for ((i=1; i<=NUM_RUNS; i++)); do
	# ändere nur Seed
        param1=$i

        # erstelle Ordner für jeden spezifischen Durchlauf (run_k_i)
        run_dir=$test_run_dir/run_${k}_${i}
        mkdir -p "$run_dir"

        # übergebe Job an SGE
        qsub -v param1=$param1,param2=$param2,param3=$param3,param4=$param4,param5=$param5,param6=$param6,param7=$param7,param8=$param8,input_file_name=$input_file_name,run_dir=$run_dir job_script.sh
    done
done

echo "All jobs submitted."
