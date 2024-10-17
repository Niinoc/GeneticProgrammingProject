# dieser Code beruht auf shell-Skripten, welche für SGE geschrieben wurden

import subprocess
import random
import os
import glob
import json
import csv

os.chdir("/home/stud/other/pi96dal/GeneticProgrammingProject/")

# Setze Pfad
log_dir = "log"

# Erstelle Verzeichnisstruktur
os.makedirs(log_dir, exist_ok=True)
test_dir = os.path.join(log_dir, "test_randomsearchVTHE_ONE")

os.makedirs(test_dir, exist_ok=True)
tested_combinations_file = os.path.join(test_dir, "tested_combinations_THE_ONE.json")

mode = 'random'  # Wechseln zwischen 'csv' und 'random'
csv_file_path = 'log/test_randomsearchV5/testdaten_randomsearchV5_gefiltert_1e-11_count_greater_than_1.csv'  # Den Pfad zur CSV-Datei angeben

input_file_list = [
    "I.6.2a",
    "I.8.14",
    "I.11.19",
    "I.27.6",
    "I.29.4",
    "I.29.16",
    "I.39.1",
    "I.50.26",
    "II.3.24",
    "II.11.28",
    "II.38.14",
    "III.9.52"
]

# Datei zur Speicherung der bereits getesteten Kombinationen
if os.path.exists(tested_combinations_file):
    with open(tested_combinations_file, "r") as file:
        tested_combinations = set(tuple(combination) for combination in json.load(file))
else:
    tested_combinations = set()


def compile_java_code():
    try:
        java_files = glob.glob("src/main/java/com/mycompany/geneticprogramming/*.java")
        subprocess.run([
                           "javac", "--release", "11", "-d", "out", "-sourcepath", "src/main/java"
                       ] + java_files, check=True)
        print("Java code compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed with error: {e}")
        exit(1)


compile_java_code()


def save_git_version():
    # Speichere Git-Version in der Log-Datei
    with open(os.path.join(test_dir, "git_version.txt"), "w") as git_file:
        subprocess.run(["git", "rev-parse", "HEAD"], stdout=git_file)
        print("Git version logged successfully.")


def check_combination(param_combination):
    # Überprüfe, ob diese Kombination bereits getestet wurde
    if param_combination in tested_combinations:
        print(f"Combination {param_combination} already tested, skipping...")
        return False, None

    param_dir_name = f"regs{param_combination[0]}_inst{param_combination[1]}_" \
                     f"popS{param_combination[2]}_gen{param_combination[3]}_" \
                     f"mutInst{param_combination[4]}_mutRegs{param_combination[5]}_" \
                     f"cross{param_combination[6]}"
    return True, param_dir_name


def submit_job(seed, param_combination, input_file_name, seed_dir_path):
    subprocess.run([
        "qsub",
        "-v",
        f"param1={seed},param2={param_combination[0]},param3={param_combination[1]},param4={param_combination[2]},"
        f"param5={param_combination[3]},param6={param_combination[4]},param7={param_combination[5]},param8={param_combination[6]},"
        f"input_file_name={input_file_name},log_dir={seed_dir_path}",
        "job_script.sh"
    ])


def run_random_mode():
    counter = 0
    skip = 0
    num_tests = 1
    # Anzahl der Läufe pro Parameterkombination
    NUM_RUNS = 50
    # Anzahl der Parameterkombinationen, die getestet werden sollen
    num_combinations = 1  # total 600
    # Manuell festgelegte Parameterbereiche
    numOfInstructions = [10]
    numOfRegisters = [5]
    populationSize = [50]
    mutationRate = [0.07]
    mutationRateRegisters = [0.2]
    crossoverRate = [0.0]
    maxFitnessEvals = [5000000]

    # Speichere den Parameter-Suchraum in einer menschenlesbaren Datei
    search_space_file = os.path.join(test_dir, "search_space_info.txt")
    with open(search_space_file, "w") as space_file:
        space_file.write("Parameter Search Space and Test Configuration\n")
        space_file.write("============================================\n\n")
        space_file.write(f"Number of Runs per Combination: {NUM_RUNS}\n")
        space_file.write(f"Total Number of Combinations: {num_combinations * num_tests}\n\n")

        space_file.write("Parameter Ranges:\n")
        space_file.write(f"numOfInstructions: {numOfInstructions}\n")
        space_file.write(f"numOfRegisters: {numOfRegisters}\n\n")

        space_file.write(f"populationSize: {populationSize}\n")
        space_file.write(f"mutationRate: {mutationRate}\n")
        space_file.write(f"mutationRateRegisters: {mutationRateRegisters}\n")
        space_file.write(f"crossoverRate: {crossoverRate}\n")
        space_file.write(f"maxFitnessEvals: {maxFitnessEvals}\n\n")

        space_file.write(f"Calculated Generations: {maxFitnessEvals} / populationSize\n")

        space_file.write("Functions Tested:\n")
        for function in input_file_list:
            space_file.write(f"- {function}\n")
        print("Search space information saved successfully.")

    # Zufällige Parameterkombinationen generieren und Jobs einreichen
    while (len(tested_combinations) < num_combinations):
        numOfInstructions_val = random.choice(numOfInstructions)
        numOfRegisters_val = random.choice(numOfRegisters)
        populationSize_val = random.choice(populationSize)
        mutationRate_val = random.choice(mutationRate)
        mutationRateRegisters_val = random.choice(mutationRateRegisters)
        crossoverRate_val = random.choice(crossoverRate)
        maxFitnessEvals_val = random.choice(maxFitnessEvals)
        numOfGenerations = int(maxFitnessEvals_val / populationSize_val)

        param_combination = (
            numOfRegisters_val,
            numOfInstructions_val,
            populationSize_val,
            numOfGenerations,
            mutationRate_val,
            mutationRateRegisters_val,
            crossoverRate_val
        )

        to_be_tested, param_dir_name = check_combination(param_combination)

        if to_be_tested:
            param_dir_path = os.path.join(test_dir, param_dir_name)

            for input_file_name in input_file_list:
                function_dir_path = os.path.join(param_dir_path, input_file_name)

                for i in range(1, NUM_RUNS + 1):
                    counter = counter +1

                    seed = i
                    seed_dir_path = os.path.join(function_dir_path, f"seed_{i}")
                    os.makedirs(seed_dir_path, exist_ok=True)

                    submit_job(seed, param_combination, input_file_name, seed_dir_path)

            # Kombination zur getesteten Menge hinzufügen
            tested_combinations.add(param_combination)

            # Aktualisiere die Liste der getesteten Kombinationen
            with open(tested_combinations_file, "w") as file:
                json.dump(list(tested_combinations), file)
        else:
            skip = skip+1
    print(counter)
    print(skip)


save_git_version()
print("All jobs submitted.")

def run_csv_mode(csv_file_path):
    counter = 0
    
    # Speichere den Parameter-Suchraum in einer menschenlesbaren Datei
    search_space_file = os.path.join(test_dir, "search_space_info.txt")
    with open(search_space_file, "w") as space_file:
        space_file.write("Parameter Search Space and Test Configuration\n")
        space_file.write("============================================\n\n")
        space_file.write(f"testing extended seed list on {csv_file_path}\n")
        space_file.write(f"testing seeds 1 to 25\n")


        space_file.write("Functions Tested:\n")
        for function in input_file_list:
            space_file.write(f"- {function}\n")
        print("Search space information saved successfully.")


    # CSV-Datei einlesen und Parameterkombinationen verarbeiten
    with open(csv_file_path, "r") as file:
        csv_reader = csv.DictReader(file, delimiter=';')

        for row in csv_reader:
            if 'parameter_combination' in row:
                params = row['parameter_combination'].split('_')
                numOfRegisters_val, numOfInstructions_val, populationSize_val, numOfGenerations, \
                    mutationRate_val, mutationRateRegisters_val, crossoverRate_val = map(float, params)
            else:
                # Ansonsten, wenn jede Spalte einzeln vorliegt:
                numOfRegisters_val = int(row['regs'])
                numOfInstructions_val = int(row['inst'])
                populationSize_val = int(row['popS'])
                numOfGenerations = int(row['gen'])
                mutationRate_val = float(row['mutInst'])
                mutationRateRegisters_val = float(row['mutRegs'])
                crossoverRate_val = float(row['cross'])

            param_combination = (
                int(numOfRegisters_val),
                int(numOfInstructions_val),
                int(populationSize_val),
                int(numOfGenerations),
                mutationRate_val,
                mutationRateRegisters_val,
                crossoverRate_val
            )

            to_be_tested, param_dir_name = check_combination(param_combination)

            if to_be_tested:
                param_dir_path = os.path.join(test_dir, param_dir_name)

                for input_file_name in input_file_list:
                    function_dir_path = os.path.join(param_dir_path, input_file_name)

                    for i in range(51, 61):  # Seeds von 11 bis 50
                        seed = i
                        seed_dir_path = os.path.join(function_dir_path, f"seed_{i}")
                        os.makedirs(seed_dir_path, exist_ok=True)
                        counter = counter +1
                        submit_job(seed, param_combination, input_file_name, seed_dir_path)

                # Kombination zur getesteten Menge hinzufügen
                tested_combinations.add(param_combination)

                # Aktualisiere die Liste der getesteten Kombinationen
                with open(tested_combinations_file, "w") as file:
                    json.dump(list(tested_combinations), file)
        print(counter)



save_git_version()
print("All CSV jobs submitted.")

if mode == 'csv':
    run_csv_mode(csv_file_path)
elif mode == 'random':
    run_random_mode()
