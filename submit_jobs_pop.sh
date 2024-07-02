#!/bin/sh

# setze Pfad
# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# kompilieren
javac -source 11 -target 11 -d out -sourcepath src/main/java src/main/java/com/mycompany/geneticprogramming/*.java

# Anzahl der Durchläufe pro Parameterwert
NUM_RUNS=2

# Manuell festgelegte Parameter
param2=5
param3=15
param4_list="10 30 50"
# 70 90 110 130 150 170 190"
param5=5000
param6=0.1
param7=0.3
param8=0.2

input_file_name=I.11.19

# erstelle Verzeichnis
log_dir=log
mkdir -p log_dir

test_dir="$log_dir/test_population_size"
mkdir -p test_dir

# erzeuge Git Version txt in log
git -C /home/stud/other/pi96dal/GeneticProgrammingProject/ rev-parse HEAD > "$test_dir/git_version.txt"

# Äußere Schleife für Parameterwerte
for param4 in $param4_list; do

    param_dir="$test_dir/pop_size_$param4"
    mkdir -p "$param_dir"

    # Innere Schleife für Durchläufe
    for i in $(seq 1 $NUM_RUNS); do
        # ändere nur Seed
        param1=$i

        # erstelle Ordner für jeden spezifischen Durchlauf (run_k_i)
        seed_dir="$param_dir/seed_${i}"
        mkdir -p "$seed_dir"

        # übergebe Job an SGE
        qsub -v param1="$param1",param2=$param2,param3=$param3,param4=$param4,param5=$param5,param6=$param6,param7=$param7,param8=$param8,input_file_name=$input_file_name,log_dir="$seed_dir", job_script.sh
    done
done

echo "All jobs submitted."
