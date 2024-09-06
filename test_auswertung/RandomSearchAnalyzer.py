import os
import re

import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend
import sympy as sp


class RandomSearchAnalyzer:
    def __init__(self, root_dir, unprocessed_combinations, allowed_functions=None):
        self.unprocessed_combinations = unprocessed_combinations
        self.root_dir = root_dir
        self.allowed_functions = allowed_functions
        self.df, self.average_df, self.test_data_df = self._process_directory()

    def _process_directory(self):
        print('processing directories')
        df_list = []
        test_data = []
        last_dir = ""  # Initialize to track changes in function_dir
        param_pattern = r"regs(\d+)_inst(\d+)_popS(\d+)_gen(\d+)_mutInst([\d\.]+)_mutRegs([\d\.]+)_cross([\d\.]+)"

        for root, dirs, files in os.walk(self.root_dir):
            # param_dir wird weiterhin extrahiert
            param_dir, function_dir, seed_dir = self._extract_directory_info(root)

            if param_dir is None:
                continue  # Skip if the directory structure is invalid

            # Split param_dir in seine Bestandteile
            match = re.findall(param_pattern, param_dir)
            if match:
                regs, inst, popS, gen, mutInst, mutRegs, cross = match[0]
            else:
                regs, inst, popS, gen, mutInst, mutRegs, cross = [None] * 7  # Fallback für unerwartete Ordnernamen

            # Zeige Fortschritt an, wenn sich das Verzeichnis ändert
            if param_dir != last_dir:
                last_dir = param_dir
                print(f"Processing directory: {last_dir}")

            # Verarbeite die best fitness Datei
            temp_df, final_function, function_generation, good_fitness = self._process_best_fitness(
                root, files, function_dir, regs, inst, popS, gen, mutInst, mutRegs, cross, seed_dir
            )

            if temp_df is not None:
                print(f"DataFrame gefunden: {temp_df.head()}")  # Debug-Ausgabe
                df_list.append(temp_df)
            else:
                print('temp_df None')

            if good_fitness and final_function is not None and function_generation is not None:
                # Extract diversity data
                start_diversity = self._extract_diversity(root, files, 'initialpopulation')
                if start_diversity != 'notfound':
                    start_diversity = f"'{round(float(start_diversity), 2)}"
                end_diversity = self._extract_diversity(root, files, 'finalpopulation')
                if end_diversity != 'notfound':
                    end_diversity = f"'{round(float(end_diversity), 2)}"

                # Die extrahierten Parameter werden in test_data eingefügt
                test_data.append([function_dir, seed_dir, final_function, start_diversity,
                                  end_diversity, function_generation, regs, inst, popS, gen, mutInst, mutRegs, cross])

        return self._compile_final_data(df_list, test_data)

    def _extract_directory_info(self, root):
        relative_path = os.path.relpath(root, self.root_dir)
        try:
            parts = relative_path.split(os.sep)
            if len(parts) < 3:
                return None, None, None

            param_dir, function_dir, seed_dir = parts[-3], parts[-2], parts[-1]

            if self.allowed_functions is not None and function_dir not in self.allowed_functions:
                return None, None, None

            if param_dir not in self.unprocessed_combinations:
                return None, None, None

            return param_dir, function_dir, seed_dir

        except ValueError:
            return None, None, None

    def _process_best_fitness(self, root, files, function_dir, regs, inst, popS, gen, mutInst, mutRegs, cross,
                              seed_dir):
        if 'out.bestfitness.txt' in files:
            file_path = os.path.join(root, 'out.bestfitness.txt')

            # Lese die Datei ein und verarbeite sie
            temp_df = pd.read_csv(file_path)

            # Statt 'param_dir' fügen wir jetzt die extrahierten Parameter hinzu
            temp_df['regs'] = regs
            temp_df['inst'] = inst
            temp_df['popS'] = popS
            temp_df['gen'] = gen
            temp_df['mutInst'] = mutInst
            temp_df['mutRegs'] = mutRegs
            temp_df['cross'] = cross
            temp_df['function'] = function_dir
            temp_df['seed'] = seed_dir
            temp_df.rename(columns={'FitnessMSE': 'fitness'}, inplace=True)

            # Bestimme, ob der letzte Fitness-Wert unter dem Schwellenwert liegt
            good_fitness = temp_df['fitness'].iloc[-1] < 1e-11
            final_function = None
            function_generation = None

            if good_fitness:
                # Extrahiere die finale Funktion, wenn der Fitnesswert gut ist
                final_function = self._extract_and_simplify_final_function(root)

                # Bestimme die Generation basierend auf dem ersten Fitness-Wert, der den Schwellenwert unterschreitet
                function_generation = temp_df[temp_df['fitness'] < 1e-11].index[0] + 1  # Generation beginnt bei 1

            return temp_df, final_function, function_generation, good_fitness

        return None, None, None, False

    @staticmethod
    def _extract_and_simplify_final_function(root):
        finalbehavior_path = os.path.join(root, 'out.finalbehavior.txt')
        if os.path.exists(finalbehavior_path):
            with open(finalbehavior_path, 'r') as f:
                first_line = f.readline().strip()
                if '# final function: ' in first_line:
                    final_function = first_line.split('# final function: ')[1]
                    sympy_expr = sp.sympify(final_function)
                    return sp.simplify(sympy_expr)
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
    def _compile_final_data(df_list, test_data):
        if not df_list:
            print("Warnung: df_list ist leer, es wurden keine gültigen DataFrames gefunden.")

        # DataFrame erstellen mit den extrahierten Parametern statt 'param_dir'
        test_data_df = pd.DataFrame(test_data, columns=[
            'function_dir', 'seed_dir', 'final_function', 'start_diversity',
            'end_diversity', 'generation', 'regs', 'inst', 'popS', 'gen',
            'mutInst', 'mutRegs', 'cross'
        ])

        print(test_data_df)

        combined_df = pd.concat(df_list, ignore_index=True)
        print(combined_df)

        # Berechne den Mittelwert der Fitness-Werte und gruppiere nach den Parametern
        mean_fitness_df = \
            combined_df.groupby(['function', 'regs', 'inst', 'popS', 'gen', 'mutInst', 'mutRegs', 'cross'])[
                'fitness'].mean().reset_index()
        print(mean_fitness_df)
        return combined_df, mean_fitness_df, test_data_df


    def _initialize_subsets(self):
        print('initializing subsets')

        # Initialize function_subsets
        for function in self.df['function'].unique():
            subset = self.df[self.df['function'] == function].copy()

            # Handle each parameter separately
            for param_col in ['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']:
                subset[param_col] = pd.to_numeric(subset[param_col], errors='coerce')
                subset[param_col] = pd.Categorical(subset[param_col], categories=sorted(subset[param_col].unique()), ordered=True)

            self.function_subsets[function] = subset

        # Initialize function_average_subsets
        for function in self.average_df['function'].unique():
            subset = self.average_df[self.average_df['function'] == function].copy()

            # Handle each parameter separately
            for param_col in ['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']:
                subset[param_col] = pd.to_numeric(subset[param_col], errors='coerce')
                subset[param_col] = pd.Categorical(subset[param_col], categories=sorted(subset[param_col].unique()), ordered=True)

            self.function_average_subsets[function] = subset

        # Initialize parameter_average_subsets by looping over each parameter
        for param_col in ['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']:
            self.parameter_average_subsets[param_col] = self.average_df[self.average_df[param_col] == param_col]

    def analyze_best_param_combinations_with_combined_metrics(self):
        # Ensure the necessary columns exist
        required_columns = ['function', 'regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate', 'generation', 'fitness']
        if not all(col in self.df.columns for col in required_columns):
            print("Error: Required columns are missing from the data.")
            return

        # Initialize a DataFrame to store all metrics
        combined_metrics_df = pd.DataFrame()

        # Iterate through each function and its subset
        for function, subset in self.function_subsets.items():
            # 1. Calculate average fitness, best fitness, and fitness improvement for each parameter combination
            metrics_df = subset.groupby(
                ['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']
            ).agg(
                avg_fitness=('fitness', 'mean'),  # Average fitness across all generations
                best_fitness=('fitness', 'min'),  # Best (lowest) fitness achieved
                fitness_improvement=('fitness', lambda x: x.iloc[0] - x.iloc[-1]),  # Improvement from first to last generation
                num_generations=('generation', 'count')  # Total number of generations
            ).reset_index()

            # 2. Count how many times each parameter combination had the best fitness over generations
            subset['best'] = subset.groupby('generation')['fitness'].transform('min') == subset['fitness']
            best_fitness_per_combination = subset[subset['best']].groupby(
                ['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']
            ).size().reset_index(name='best_fitness_count')

            # 3. Merge the best_fitness_count with the metrics dataframe
            combined_df = pd.merge(metrics_df, best_fitness_per_combination, on=['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate'], how='left')
            combined_df['best_fitness_count'].fillna(0, inplace=True)  # Fill NaN values with 0

            # Add the function column for context
            combined_df['function'] = function

            # Append the result to the overall DataFrame
            combined_metrics_df = pd.concat([combined_metrics_df, combined_df], ignore_index=True)

        # Sort the results by both best fitness and best_fitness_count (or other metrics)
        sorted_combined_metrics_df = combined_metrics_df.sort_values(by=['best_fitness', 'best_fitness_count', 'avg_fitness'], ascending=[True, False, True])

        # Display the top parameter combinations
        print("Top parameter combinations based on combined metrics (best fitness count, avg fitness, and best fitness):")
        for function in sorted_combined_metrics_df['function'].unique():
            print(f"\nFunction: {function}")
            print(sorted_combined_metrics_df[sorted_combined_metrics_df['function'] == function].head(10))  # Show top 10 combinations

        # Optionally, save to CSV
        sorted_combined_metrics_df.to_csv('combined_metrics_best_param_combinations.csv', index=False, sep=';')
        print("Results saved to 'combined_metrics_best_param_combinations.csv'")

        return sorted_combined_metrics_df

    def analyze_local_optima_stagnation(self, improvement_threshold=0.01, window_size=10):
        # Initialize a DataFrame to store stagnation metrics
        stagnation_df = pd.DataFrame()

        # Iterate through each function and its subset
        for function, subset in self.function_subsets.items():
            subset = subset.copy()

            # Calculate the fitness improvement between consecutive generations
            subset['fitness_diff'] = subset.groupby(['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate'])['fitness'].diff()

            # Identify stagnation: When the fitness improvement is less than the threshold
            subset['stagnant'] = subset['fitness_diff'].abs() < improvement_threshold

            # Calculate the number of consecutive generations with no significant improvement (stagnation)
            subset['stagnation_streak'] = subset.groupby(['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate'])['stagnant'].cumsum()

            # Identify cases where the combination has been stagnant for more than `window_size` generations
            stagnant_combinations = subset.groupby(['regs', 'inst', 'pop_size', 'mut_inst', 'mut_regs', 'cross_rate']).apply(
                lambda x: (x['stagnation_streak'] >= window_size).sum()
            ).reset_index(name='stagnation_count')

            # Add the function to the results
            stagnant_combinations['function'] = function

            # Append to the main DataFrame
            stagnation_df = pd.concat([stagnation_df, stagnant_combinations], ignore_index=True)

        # Sort by the number of generations in stagnation
        stagnation_df = stagnation_df.sort_values(by=['function', 'stagnation_count'], ascending=[True, False])

        # Display the top combinations with the most stagnation
        print("Parameter combinations with the most stagnation (stuck in local optima):")
        for function in stagnation_df['function'].unique():
            print(f"\nFunction: {function}")
            print(stagnation_df[stagnation_df['function'] == function].head())

        # Optionally save to CSV
        stagnation_df.to_csv('stagnation_metrics.csv', index=False, sep=';')
        print("Stagnation results saved to 'stagnation_metrics.csv'")

        return stagnation_df



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

