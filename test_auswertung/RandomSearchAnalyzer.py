import os
import re
import math
import signal

import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
from matplotlib import pyplot as plt
import sympy as sp


class RandomSearchAnalyzer:
    def __init__(self, root_dir, unprocessed_combinations, allowed_functions=None):
        self.mse_threshold = 1e-11
        self.unprocessed_combinations = unprocessed_combinations
        # Prüfen, ob es unprocessed_combinations gibt
        if len(self.unprocessed_combinations) < 1:
            print("Info: All combinations have been processed. No further actions will be taken.")
            return  # Abbrechen der Initialisierung

        self.param_pattern = r"regs(\d+)_inst(\d+)_popS(\d+)_gen(\d+)_mutInst([\d\.]+)_mutRegs([\d\.]+)_cross([\d\.]+)"
        self.root_dir = root_dir
        self.allowed_functions = allowed_functions
        self.test_data_df = self._process_directory()

    def _process_directory(self):
        print('processing directories')
        df_list = []
        test_data = []
        last_dir = ""  # Initialize to track changes in function_dir
        param_count = 0

        for root, dirs, files in os.walk(self.root_dir):
            param_dir, function_dir, seed_dir, param_values = self._extract_directory_info(root)

            if param_dir is None:
                continue  # Skip if the directory structure is invalid

            # Zeige Fortschritt an, wenn sich das Verzeichnis ändert
            if param_dir != last_dir:
                last_dir = param_dir
                param_count += 1
                print(
                    f"Processing directory: {param_values}, {round((param_count / len(self.unprocessed_combinations)) * 100, 2)}%")

            # Verarbeite die best fitness Datei
            temp_df, final_function, function_generation, good_fitness, final_fitness, stagnation_percentage = self._process_best_fitness(
                root, files, function_dir, param_values, seed_dir
            )
            # print(function_dir)

            #if temp_df is not None:
                #df_list.append(temp_df)
            #else:
                #print('temp_df None')

            # if not good_fitness:
            #     final_function = 'noSolution'
            #     function_generation = 'noSolution'
            # Extract diversity data
            start_diversity = self._extract_diversity(root, files, 'initialpopulation')
            if start_diversity != 'notfound':
                start_diversity = round(float(start_diversity), 2)
            end_diversity = self._extract_diversity(root, files, 'finalpopulation')
            if end_diversity != 'notfound':
                end_diversity = round(float(end_diversity), 2)

            # Die extrahierten Parameter werden in test_data eingefügt
            test_data.append(
                [good_fitness, function_dir, final_function, final_fitness, stagnation_percentage, start_diversity,
                 end_diversity, function_generation, param_values[0], param_values[1], param_values[2],
                 param_values[3], param_values[4], param_values[5], param_values[6], seed_dir])

        return self._compile_final_data(test_data)

    def _extract_directory_info(self, root):
        relative_path = os.path.relpath(root, self.root_dir)

        try:
            parts = relative_path.split(os.sep)
            if len(parts) < 3:
                return None, None, None, None
            # print(relative_path)
            param_dir, function_dir, seed_dir = parts[-3], parts[-2], parts[-1]
            # print('param_dir: ' + param_dir + ' function_dir: ' + function_dir + ' seed_dir: ' + seed_dir)
            if self.allowed_functions is not None and function_dir not in self.allowed_functions:
                return None, None, None, None

            # Split param_dir in seine Bestandteile
            match = re.findall(self.param_pattern, param_dir)
            if match:
                regs, inst, popS, gen, mutInst, mutRegs, cross = match[0]
            else:
                regs, inst, popS, gen, mutInst, mutRegs, cross = [None] * 7  # Fallback für unerwartete Ordnernamen

            param_values = [
                int(regs),
                int(inst),
                int(popS),
                int(gen),
                float(mutInst),
                float(mutRegs),
                float(cross)
            ]

            def compare_with_tolerance(list1, list2, tol=1e-5):
                if len(list1) != len(list2):
                    return False
                return all(
                    math.isclose(a, b, abs_tol=tol) if isinstance(a, float) and isinstance(b, float) else a == b
                    for a, b in zip(list1, list2)
                )

            # param_dir -> self.unprocessed_combinations format
            for combination in self.unprocessed_combinations:
                # print('param_values: '+str(param_values))
                # print('combination: '+str(combination))
                if compare_with_tolerance(param_values, combination):
                    # print('found!')
                    return param_dir, function_dir, seed_dir, param_values
            # print('notfound')
            return None, None, None, None

        except ValueError:
            return None, None, None, None

    def _process_best_fitness(self, root, files, function_dir, param_values,
                              seed_dir):
        if 'out.bestfitness.txt' in files:
            file_path = os.path.join(root, 'out.bestfitness.txt')
            temp_df = pd.read_csv(file_path)
            # print(temp_df)

            temp_df['regs'] = param_values[0]
            temp_df['inst'] = param_values[1]
            temp_df['popS'] = param_values[2]
            temp_df['gen'] = param_values[3]
            temp_df['mutInst'] = param_values[4]
            temp_df['mutRegs'] = param_values[5]
            temp_df['cross'] = param_values[6]
            temp_df['function'] = function_dir
            temp_df['seed'] = seed_dir
            temp_df.rename(columns={'FitnessMSE': 'fitness'}, inplace=True)

            # Berechne die Fitness-Differenz (Ableitung) zwischen den Generationen
            temp_df['fitness_derivative'] = temp_df['fitness'].diff()
            # Setze den ersten Ableitungswert auf 0 (keine Änderung für die erste Generation)
            temp_df['fitness_derivative'] = temp_df['fitness_derivative'].fillna(0)
            # Definiere den Stagnations-Schwellenwert
            # stagnation_threshold = 1e-11
            # Identifiziere Stagnation: Wenn die Änderung gleich 0.0
            temp_df['is_stagnant'] = temp_df['fitness_derivative'].abs() == 0.0

            # Berechne die Stagnationsrate (prozentualer Anteil der Generationen, die stagnieren)
            stagnation_count = temp_df['is_stagnant'].sum()
            stagnation_percentage = (stagnation_count / param_values[3]) * 100

            # Bestimme, ob der letzte Fitness-Wert unter dem Schwellenwert liegt
            final_fitness = temp_df['fitness'].iloc[-1]
            good_fitness = final_fitness < self.mse_threshold
            function_generation = temp_df['generation'].iloc[-1]

            # Extrahiere die finale Funktion, wenn der Fitnesswert gut ist
            final_function = self._extract_and_simplify_final_function(root)
            if good_fitness:
                # Bestimme die Generation basierend auf dem ersten Fitness-Wert, der den Schwellenwert unterschreitet
                function_generation = temp_df[temp_df['fitness'] < self.mse_threshold].index[
                                          0] + 1  # Generation beginnt bei 1

            return temp_df, final_function, function_generation, good_fitness, final_fitness, stagnation_percentage

        return None, None, None, False, None, None
    
    def handler(signum, frame):
        raise TimeoutError("Die Vereinfachung dauert zu lange")
    
    signal.signal(signal.SIGALRM, handler)

    @staticmethod
    def _extract_and_simplify_final_function(root):
        finalbehavior_path = os.path.join(root, 'out.finalbehavior.txt')
        if os.path.exists(finalbehavior_path):
            with open(finalbehavior_path, 'r') as f:
                first_line = f.readline().strip()
                if '# final function: ' in first_line:
                    final_function = first_line.split('# final function: ')[1]
                    try:
                        # Timeout auf 10 Sekunden setzen
                        signal.alarm(120)

                        # Versuch, den Ausdruck zu sympify-en und zu simplifizieren
                        sympy_expr = sp.sympify(final_function)
                        result = sp.simplify(sympy_expr)

                        # Timeout deaktivieren, falls der Prozess erfolgreich war
                        signal.alarm(0)
                        return result
                    
                    except TimeoutError:
                        # Timeout erreicht, gebe die Originalfunktion zurück
                        print("Timeout: Die Vereinfachung hat zu lange gedauert.")
                        return final_function

                    except (ZeroDivisionError, sp.SympifyError, ValueError, TypeError, OverflowError) as e:
                        # Bei mathematischen Fehlern die Originalfunktion zurückgeben
                        print(f"Fehler beim Vereinfachen: {e}. Gebe die Originalfunktion zurück.")
                        return final_function

                    finally:
                        # Timeout deaktivieren, um sicherzustellen, dass keine weiteren Alarme gesetzt sind
                        signal.alarm(0)
        return None

    @staticmethod
    def _extract_diversity(root, files, population_type):
        diversity = 'notfound'
        if f'out.{population_type}.txt' in files:
            population_path = os.path.join(root, f'out.{population_type}.txt')
            with open(population_path, 'r') as f:
                first_line = f.readline().strip()
                if 'Diversity: ' in first_line:
                    diversity = first_line.split('Diversity: ')[1]
                else:
                    lines = f.readlines()
                    last_line = lines[-1].strip()
                    if 'Diversity: ' in last_line:
                        diversity = last_line.split('Diversity: ')[1]
        return diversity

    @staticmethod
    def _compile_final_data(test_data):
        #if not df_list:
            #print("Warnung: df_list ist leer, es wurden keine gültigen DataFrames gefunden.")

        #combined_df = pd.concat(df_list, ignore_index=True)

        #print(combined_df)
        # Berechne den Mittelwert der Fitness-Werte und gruppiere nach den Parametern
        #mean_fitness_df = \
            #combined_df.groupby(['function', 'regs', 'inst', 'popS', 'gen', 'mutInst', 'mutRegs', 'cross'])[
                #'fitness'].mean().reset_index()

        #print(mean_fitness_df)

        # DataFrame erstellen mit den extrahierten Parametern statt 'param_dir'
        test_data_df = pd.DataFrame(test_data, columns=[
            'good_fitness', 'function_dir', 'final_function', 'final_fitness', 'stagnation', 'start_diversity',
            'end_diversity', 'found_generation', 'regs', 'inst', 'popS', 'gen',
            'mutInst', 'mutRegs', 'cross', 'seed_dir'
        ])

        # print(test_data_df)
        # print(combined_df)
        # print(mean_fitness_df)
        return test_data_df

    def _get_output_dir(self, param_dir):
        return os.path.join(self.root_dir, param_dir)

    def save_test_data_for_function(self, function):
        filtered_df = self.test_data_df[self.test_data_df['function_dir'] == function]

        output_dir = self._get_output_dir(function)
        filename = f"{function}_testdata.csv"
        testdata_path = os.path.join(output_dir, filename)

        filtered_df.to_csv(testdata_path, index=False, sep=';')
        print(f"Datei wurde gespeichert: {filename}")

    def save_test_data(self):
        try:
            output_dir = self.root_dir
            filename = f"{os.path.basename(self.root_dir)}_testdata.csv"
            testdata_path = os.path.join(output_dir, filename)

            # Prüfe, ob die Datei bereits existiert
            file_exists = os.path.isfile(testdata_path)

            # Speichere die Daten; falls die Datei bereits existiert, ohne Header anhängen
            self.test_data_df.to_csv(testdata_path, mode='a' if file_exists else 'w', header=not file_exists,
                                     index=False, sep=';')

            if file_exists:
                print(f"Daten wurden an die Datei angehängt: {filename}")
            else:
                print(f"Datei wurde neu erstellt: {filename}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")

    def plot_fitness_for_function_and_params(self, function, regs, inst, popS, gen, mutInst, mutRegs, cross):
        # Filtere das DataFrame nach der gewünschten Funktion und Parameterkombination
        filtered_df = self.df[
            (self.df['function'] == function) &
            (self.df['regs'] == regs) &
            (self.df['inst'] == inst) &
            (self.df['popS'] == popS) &
            (self.df['gen'] == gen) &
            (self.df['mutInst'] == mutInst) &
            (self.df['mutRegs'] == mutRegs) &
            (self.df['cross'] == cross)
            ]

        # Gruppiere nach Seed, um für jeden Seed einen Fitness-Verlauf zu zeichnen
        plt.figure(figsize=(10, 6))  # Erstelle eine neue Figur mit einer bestimmten Größe
        sns.lineplot(data=filtered_df, x='generation', y='fitness', hue='seed', palette='tab10')

        # Beschriftungen und Titel hinzufügen
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title(
            f'Fitness-Verlauf für Funktion: {function}, Params: ({regs}, {inst}, {popS}, {mutInst}, {mutRegs}, {cross})')
        plt.grid(True)
        plt.savefig('plot_test.png')
        plt.close()
