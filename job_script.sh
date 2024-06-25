#!/bin/bash
#$ -cwd
#$ -o /dev/null
#$ -e /dev/null

# Lade die übergebenen Parameter
param1=$param1
param2=$param2
param3=$param3
param4=$param4
param5=$param5
param6=$param6
param7=$param7
param8=$param8
input_file_name=$input_file_name
run_dir=$run_dir

# Java-Programm ausführen
echo "Starting Java program for test $param1 with parameters: $param1 $param2 $param3 $param4 $param5 $param6 $param7 $param8"

java -cp out com.mycompany.geneticprogramming.GeneticProgramming $param1 $param2 $param3 $param4 $param5 $param6 $param7 $param8 $input_file_name

# kopiere Ausgabedateien aus log-Ordner in aktuellen Durchlauf-Ordner
cp log/out.bestfitness.txt "$run_dir/out.bestfitness.txt"
cp log/out.finalbehavior.txt "$run_dir/out.finalbehavior.txt"
cp log/out.finalpopulation.txt "$run_dir/out.finalpopulation.txt"
cp log/out.finalprogram.txt "$run_dir/out.finalprogram.txt"
cp log/fitnessFunction.txt "$run_dir/fitnessFunction.txt"
cp log/initialbehavior.txt "$run_dir/initialbehavior.txt"
cp log/initialpopulation.txt "$run_dir/initialpopulation.txt"
cp log/parameters.txt "$run_dir/parameters.txt"

# kopiere Eingabe-Datei in aktuellen Durchlauf-Ordner
cp "in/in.$input_file_name.txt" "$run_dir/in.$input_file_name.txt"

echo "Job completed."
