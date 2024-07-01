#!/bin/sh
#$ -cwd
#$ -o /dev/null
#$ -e /dev/null

# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# Java-Programm ausführen
java -cp out com.mycompany.geneticprogramming.GeneticProgramming $param1 $param2 $param3 $param4 $param5 $param6 $param7 $param8 $input_file_name

# kopiere Ausgabedateien aus log-Ordner in aktuellen Durchlauf-Ordner
cp log/out.bestfitness.txt "$run_dir/out.bestfitness.txt"
cp log/out.finalbehavior.txt "$run_dir/out.finalbehavior.txt"
cp log/out.finalpopulation.txt "$run_dir/out.finalpopulation.txt"
cp log/out.finalprogram.txt "$run_dir/out.finalprogram.txt"
cp log/out.fitnessFunction.txt "$run_dir/out.fitnessFunction.txt"
cp log/out.initialbehavior.txt "$run_dir/out.initialbehavior.txt"
cp log/out.initialpopulation.txt "$run_dir/out.initialpopulation.txt"
cp log/out.parameters.txt "$run_dir/out.parameters.txt"

# kopiere Eingabe-Datei in aktuellen Durchlauf-Ordner
cp "in/in.$input_file_name.txt" "$run_dir/in.$input_file_name.txt"
