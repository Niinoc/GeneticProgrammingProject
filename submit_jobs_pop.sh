#!/bin/sh

# setze Pfad
# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# kompilieren
# javac -source 17 -target 11 -d out -sourcepath src/main/java src/main/java/com/mycompany/geneticprogramming/*.java

# Anzahl der Durchläufe pro Test
NUM_RUNS=50

# Manuell festgelegte Parameter
numOfInputs=5
numOfInstructions=15
# Liste der populationSize Werte
populationSize_list="10 30 50 70 100 125 150 175 200 225 250 275 300 400 500"
numOfGenerations=25000
mutationRate=0.03
mutationRateRegisters=0.3
mutationStrengthRegisters=0.2

input_file_list="I.8.14 I.11.19 I.27.6 I.29.4 I.39.1 I.50.26 II.3.24 II.11.28 II.38.14"

# erstelle Verzeichnis
log_dir=log
mkdir -p $log_dir

test_dir="$log_dir/test_population_size"
mkdir -p $test_dir

# erzeuge Git Version txt in log
git -C /home/stud/other/pi96dal/GeneticProgrammingProject/ rev-parse HEAD > "$test_dir/git_version.txt"

for input_file_name in $input_file_list; do

    # erstelle Ordner für die spezifische Input Funktion
    function_dir="$test_dir/$input_file_name"
    mkdir -p "$function_dir"
    
    # Äußere Schleife für Parameterwerte
    for populationSize in $populationSize_list; do

        # erstelle Ordner für jeden Parameterwert
        param_dir="$function_dir/$populationSize"
        mkdir -p "$param_dir"

        # Innere Schleife für Durchläufe
        for i in $(seq 1 $NUM_RUNS); do
            # ändere nur Seed
            seed=$i

            # erstelle Ordner für jeden spezifischen seed
            seed_dir="$param_dir/seed_${i}"
            mkdir -p "$seed_dir"
            
            # übergebe Job an SGE
            qsub -v param1="$seed",param2=$numOfInputs,param3=$numOfInstructions,param4=$populationSize,param5=$numOfGenerations,param6=$mutationRate,param7=$mutationRateRegisters,param8=$mutationStrengthRegisters,input_file_name=$input_file_name,log_dir="$seed_dir", job_script.sh
        done
    done
done

echo "All jobs submitted."
