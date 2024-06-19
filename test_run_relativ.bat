@echo off
setlocal enabledelayedexpansion

REM Anzahl der Durchläufe pro Test
set NUM_RUNS=3

REM Anzahl der Tests
set NUM_TESTS=3

REM Manuell festgelegte Parameter
set param2=5
set param3=15
set param4=150
set param5=1000
set param6=0.1
set param7=0.3
set param8=0.1

REM Setze den Namen des Input-Datei-Präfix
set input_file_name=I.11.19

REM Definiere den Hauptordner für die Tests
set test_dir=test_population_size

REM Compile Java files
javac -d out -sourcepath src\main\java src\main\java\com\mycompany\geneticprogramming\*.java

REM Äußere Schleife für Tests
for /L %%k in (1, 1, %NUM_TESTS%) do (

    set /A "param4=(10+(%%k*20))"

    REM Erstelle den Ordner für jeden Testlauf (run_%%k)
    set test_run_dir=%test_dir%\run_%%k
    mkdir "!test_run_dir!"

    REM Innere Schleife für Durchläufe
    for /L %%i in (1, 1, %NUM_RUNS%) do (

        set param1=%%i

        REM Erstelle den Ordner für jeden spezifischen Durchlauf (run_%%k_%%i)
        set run_dir=!test_run_dir!\run_%%k_%%i
        mkdir "!run_dir!"

        REM Java-Programm mit den festgelegten Parametern starten
        echo Starte Java-Programm für Test %%k, Durchlauf %%i
        echo Parameter: !param1! !param2! !param3! !param4! !param5! !param6! !param7! !param8!

        java -cp out com.mycompany.geneticprogramming.GeneticProgramming !param1! !param2! !param3! !param4! !param5! !param6! !param7! !param8! !input_file_name!

        REM Kopiere die Ausgabedateien aus dem log-Ordner in den aktuellen Durchlauf-Ordner
        copy log\out.bestfitness.txt "!run_dir!\out.bestfitness.txt"
        copy log\out.finalbehavior.txt "!run_dir!\out.finalbehavior.txt"
        copy log\out.finalpopulation.txt "!run_dir!\out.finalpopulation.txt"
        copy log\out.finalprogram.txt "!run_dir!\out.finalprogram.txt"
        copy log\out.fitnessFunction.txt "!run_dir!\out.fitnessFunction.txt"
        copy log\out.initialbehavior.txt "!run_dir!\out.initialbehavior.txt"
        copy log\out.initialpopulation.txt "!run_dir!\out.initialpopulation.txt"
        copy log\out.parameters.txt "!run_dir!\out.parameters.txt"
        
        REM Kopiere die Eingabe-Datei in den aktuellen Durchlauf-Ordner
        copy "in\in.%input_file_name%.txt" "!run_dir!\in.%input_file_name%.txt"
    )
)

echo All runs completed.
pause

endlocal
