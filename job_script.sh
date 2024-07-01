#!/bin/sh
#$ -cwd
#$ -o /dev/null
#$ -e /dev/null

# shellcheck disable=SC2164
cd /home/stud/other/pi96dal/GeneticProgrammingProject/

# Java-Programm ausführen
java -cp out com.mycompany.geneticprogramming.GeneticProgramming $param1 $param2 $param3 $param4 $param5 $param6 $param7 $param8 $input_file_name $log_dir
