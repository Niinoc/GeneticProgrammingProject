#!/bin/sh

# setze Pfad
# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# kompilieren
javac -source 17 -target 11 -d out -sourcepath src/main/java src/main/java/com/mycompany/geneticprogramming/*.java

# Anzahl der Durchläufe pro Test
NUM_RUNS=100

# Anzahl der Tests
# hier durch param6 list gegeben

# Manuell festgelegte Parameter
param2=5
param3=15
param4=130
param5=25000
# Liste der param6 Werte
param6_list="0.01 0.03 0.05 0.07 0.09 0.15 0.2 0.25 0.3 0.35"
# "0.02 0.03 0.04 0.05 0.06 0.07 0.08 0.09"
param7=0.3
param8=0.2

input_file_list="I.11.19 I.29.4 I.39.1 I.8.14"

# erstelle Verzeichnis
log_dir=log
mkdir -p $log_dir

test_dir="$log_dir/test_mutation_rate_multi"
mkdir -p $test_dir

# erzeuge Git Version txt in log
git -C /home/stud/other/pi96dal/GeneticProgrammingProject/ rev-parse HEAD > "$test_dir/git_version.txt"

for input_file_name in $input_file_list; do
    # Äußere Schleife für Parameterwerte
    for param6 in $param6_list; do

        # erstelle Ordner für jeden Parameterwert
        param_dir="$test_dir/$param6"
        mkdir -p "$param_dir"

        # Innere Schleife für Durchläufe
        for i in $(seq 1 $NUM_RUNS); do
            # ändere nur Seed
            param1=$i

            # erstelle Ordner für jeden spezifischen seed
            seed_dir="$param_dir/seed_${i}"
            mkdir -p "$seed_dir"
            
            # erstelle Ordner für die spezifische Input Funktion
            function_dir="$seed_dir/$input_file_name"
            mkdir -p "$function_dir"

            # übergebe Job an SGE
            qsub -v param1="$param1",param2=$param2,param3=$param3,param4=$param4,param5=$param5,param6=$param6,param7=$param7,param8=$param8,input_file_name=$input_file_name,log_dir="$function_dir", job_script.sh
        done
    done
done

echo "All jobs submitted."

