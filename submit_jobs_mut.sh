#!/bin/sh

# setze Pfad
# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# kompilieren
javac -d out -sourcepath src/main/java src/main/java/com/mycompany/geneticprogramming/*.java

# Anzahl der Durchläufe pro Test
NUM_RUNS=2

# Anzahl der Tests
# hier durch param6 list gegeben

# Manuell festgelegte Parameter
param2=5
param3=15
param4=100
param5=5000
# Liste der param6 Werte
param6_list="0.01 0.05"
# 0.1 0.15 0.2 0.25 0.3 0.35
param7=0.3
param8=0.2

input_file_name=I.11.19

# Hauptordner für die Tests
test_dir=test_mutation_rate

# erstelle Verzeichnis
mkdir -p "$test_dir"

# erzuege Git Version txt in test_dir
git -C /home/stud/other/pi96dal/GeneticProgrammingProject/ rev-parse HEAD > "$test_dir/git_version.txt"

# Äußere Schleife für Tests
for param6 in $param6_list; do

    # erstelle Ordner für jeden Testlauf (run_k)
    test_run_dir="$test_dir/run_${param6}"
    mkdir -p "$test_run_dir"

    # Innere Schleife für Durchläufe
    for i in $(seq 1 $NUM_RUNS); do
        # ändere nur Seed
        param1=$i

        # erstelle Ordner für jeden spezifischen Durchlauf (run_k_i)
        run_dir="$test_run_dir/run_${param6}_${i}"
        mkdir -p "$run_dir"

        log_dir="log/$run_dir"
        mkdir -p "$log_dir"

        # übergebe Job an SGE
        qsub -v param1="$param1",param2=$param2,param3=$param3,param4=$param4,param5=$param5,param6=$param6,param7=$param7,param8=$param8,input_file_name=$input_file_name,log_dir="$log_dir",run_dir="$run_dir" job_script.sh
    done
done

echo "All jobs submitted."

