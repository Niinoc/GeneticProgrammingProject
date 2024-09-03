import subprocess
import random
import os
import glob
import json

# Setze Pfad
os.chdir("/home/stud/other/pi96dal/GeneticProgrammingProject/")

# Erstelle Verzeichnisstruktur
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

test_dir = os.path.join(log_dir, "test_randomsearchV1")
os.makedirs(test_dir, exist_ok=True)

# Datei zur Speicherung der bereits getesteten Kombinationen
tested_combinations_file = os.path.join(test_dir, "tested_combinations.json")

# Lade bereits getestete Kombinationen
if os.path.exists(tested_combinations_file):
    with open(tested_combinations_file, "r") as file:
        tested_combinations = set(tuple(combination) for combination in json.load(file))
else:
    tested_combinations = set()


# Kompilierungsschritt hinzufügen (mit korrektem Pfad)
try:
    java_files = glob.glob("src/main/java/com/mycompany/geneticprogramming/*.java")
    subprocess.run([
        "javac", "--release", "11", "-d", "out", "-sourcepath", "src/main/java"
    ] + java_files, check=True)
    print("Java code compiled successfully.")
except subprocess.CalledProcessError as e:
    print(f"Compilation failed with error: {e}")
    exit(1)

# Anzahl der Läufe pro Parameterkombination
NUM_RUNS = 10
# Anzahl der Parameterkombinationen, die getestet werden sollen
num_combinations = 700
# Manuell festgelegte Parameterbereiche
numOfInstructions = [10, 15, 20, 25, 30, 35, 40, 50, 100]
populationSize = [50, 100, 150, 200, 250, 300, 500, 1000, 2500, 5000]
mutationRate = [0.05, 0.07, 0.09, 0.15, 0.2, 0.3, 0.4, 0.5]
mutationRateRegisters = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
crossoverRate = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.7]
maxFitnessEvals = 5000000

input_file_list = [
    #"I.6.2a",
    "I.8.14",
    "I.11.19",
    "II.11.28",
    #"III.9.52"
]



# Speichere Git-Version in der Log-Datei
with open(os.path.join(test_dir, "git_version.txt"), "w") as git_file:
    subprocess.run(["git", "rev-parse", "HEAD"], stdout=git_file)
    print("Git version logged successfully.")

# Zufällige Parameterkombinationen generieren und Jobs einreichen
for _ in range(num_combinations):
    numOfInstructions_val = random.choice(numOfInstructions)
    numOfRegisters_val = numOfInstructions_val
    populationSize_val = random.choice(populationSize)
    mutationRate_val = random.choice(mutationRate)
    mutationRateRegisters_val = random.choice(mutationRateRegisters)
    crossoverRate_val = random.choice(crossoverRate)
    numOfGenerations = int(maxFitnessEvals / populationSize_val)

    # Erzeuge eine eindeutige Kennung für die Kombination
    param_combination = (
        numOfRegisters_val,
        numOfInstructions_val,
        populationSize_val,
        numOfGenerations,
        mutationRate_val,
        mutationRateRegisters_val,
        crossoverRate_val
    )

    # Überprüfe, ob diese Kombination bereits getestet wurde
    if param_combination in tested_combinations:
        print(f"Combination {param_combination} already tested, skipping...")
        continue

    # Führe den Test durch
    param_dir_name = f"regs{numOfRegisters_val}_inst{numOfInstructions_val}_" \
                     f"popS{populationSize_val}_gen{numOfGenerations}_" \
                     f"mutInst{mutationRate_val}_mutRegs{mutationRateRegisters_val}_" \
                     f"cross{crossoverRate_val}"

    param_dir_path = os.path.join(test_dir, param_dir_name)

    for input_file_name in input_file_list:
        function_dir_path = os.path.join(param_dir_path, input_file_name)

        for i in range(1, NUM_RUNS + 1):
            seed = i
            seed_dir_path = os.path.join(function_dir_path, f"seed_{i}")
            os.makedirs(seed_dir_path, exist_ok=True)

            subprocess.run([
                "qsub", 
                "-v",
                f"param1={seed},param2={numOfRegisters_val},param3={numOfInstructions_val},param4={populationSize_val},"
                f"param5={numOfGenerations},param6={mutationRate_val},param7={mutationRateRegisters_val},param8={crossoverRate_val},"
                f"input_file_name={input_file_name},log_dir={seed_dir_path}",
                "job_script.sh"
            ])


    # Kombination zur getesteten Menge hinzufügen
    tested_combinations.add(param_combination)

    # Aktualisiere die Liste der getesteten Kombinationen
    with open(tested_combinations_file, "w") as file:
        json.dump(list(tested_combinations), file)

print("All jobs submitted.")
