import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend
import sympy as sp


class RandomSearchAnalyzer:
    def __init__(self, root_dir, allowed_functions=None):
        self.root_dir = root_dir
        self.allowed_functions = allowed_functions

        self.df, self.average_df, self.test_data_df = self._process_directory()
        self.function_subsets = {}
        self.function_average_subsets = {}
        self.parameter_average_subsets = {}
        self._initialize_subsets()

    def _process_directory(self):
        print('processing directories')
        df_list = []
        test_data = []
        last_dir = ""  # Initialize to track changes in function_dir

        for root, dirs, files in os.walk(self.root_dir):
            # Initialize directory-related variables before processing files
            function_dir, param_dir, seed_dir = self._extract_directory_info(root)

            if function_dir is None:
                continue  # Skip if the directory structure is invalid

            # Display progress by printing the current function_dir if it has changed
            if function_dir != last_dir:
                last_dir = function_dir
                print(f"Processing directory: {last_dir}")

            # Process the best fitness file
            temp_df, final_function, function_generation, good_fitness = self._process_best_fitness(root, files,
                                                                                                    function_dir,
                                                                                                    param_dir, seed_dir)

            if temp_df is not None:
                df_list.append(temp_df)
            else:
                print('temp_df None')

            if good_fitness and final_function is not None and function_generation is not None:
                # Extract diversity data
                start_diversity = self._extract_diversity(root, files, 'initialpopulation')
                if start_diversity != 'notfound': start_diversity = f"'{round(float(start_diversity), 2)}"
                end_diversity = self._extract_diversity(root, files, 'finalpopulation')
                if end_diversity != 'notfound': end_diversity = f"'{round(float(end_diversity), 2)}"

                # Compile test data if all conditions are met
                test_data.append([function_dir, param_dir, seed_dir, final_function, start_diversity,
                                  end_diversity, function_generation])

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

            return function_dir, param_dir, seed_dir
        except ValueError:
            return None, None, None

    def _process_best_fitness(self, root, files, function_dir, param_dir, seed_dir):
        if 'out.bestfitness.txt' in files:
            file_path = os.path.join(root, 'out.bestfitness.txt')

            def skip_rows(index):
                # Lade alle Zeilen für die ersten 1000 Generationen
                if index < 1000:
                    return False
                # Danach nur gerade Generationen laden
                return index % 2 != 0

            # Laden der CSV-Datei mit der spezifischen skiprows-Funktion
            # TODO: Sinnhaftigkeit überprüfen ^
            temp_df = pd.read_csv(file_path)  # ,skiprows = skip_rows

            temp_df['function'] = function_dir
            temp_df['parameter'] = param_dir
            temp_df['seed'] = seed_dir
            temp_df.rename(columns={'FitnessMSE': 'fitness'}, inplace=True)

            good_fitness = temp_df['fitness'].iloc[-1] < 1e-11
            final_function = None
            function_generation = None

            if good_fitness:
                final_function = self._extract_and_simplify_final_function(root)
                # Since good_fitness is True, we can safely use the last index as the generation
                function_generation = temp_df[temp_df['fitness'] < 1e-11].index[0] + 1  # generation starts on
                # 1, index on 0

            return temp_df, final_function, function_generation, good_fitness
        return None, None, False

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
            if os.path.exists(population_path):
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

        test_data_df = pd.DataFrame(test_data, columns=['function_dir', 'param_dir', 'seed_dir', 'final_function',
                                                        'start_diversity', 'end_diversity', 'generation'])
        print(test_data_df)

        combined_df = pd.concat(df_list, ignore_index=True)
        print(combined_df)

        mean_fitness_df = combined_df.groupby(['function', 'parameter', 'generation'])['fitness'].mean().reset_index()
        print(mean_fitness_df)
        return combined_df, mean_fitness_df, test_data_df

    def _initialize_subsets(self):
        print('initializing subsets')
        # Initialize function_subsets
        for function in self.df['function'].unique():
            subset = self.df[self.df['function'] == function].copy()
            subset['parameter'] = pd.to_numeric(subset['parameter'], errors='coerce')
            subset['parameter'] = pd.Categorical(subset['parameter'], categories=sorted(subset['parameter'].unique()),
                                                 ordered=True)
            self.function_subsets[function] = subset

        # Initialize function_average_subsets
        for function in self.average_df['function'].unique():
            subset = self.average_df[self.average_df['function'] == function].copy()
            subset['parameter'] = pd.to_numeric(subset['parameter'], errors='coerce')
            subset['parameter'] = pd.Categorical(subset['parameter'], categories=sorted(subset['parameter'].unique()),
                                                 ordered=True)
            self.function_average_subsets[function] = subset

        # Initialize parameter_average_subsets
        for parameter in self.average_df['parameter'].unique():
            self.parameter_average_subsets[parameter] = self.average_df[self.average_df['parameter'] == parameter]

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

            self.test_data_df.to_csv(testdata_path, index=False, sep=';')
            print(f"Datei wurde gespeichert: {filename}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")

    def save_all_test_data(self):
        functions_to_process = self.allowed_functions if self.allowed_functions is not None else self.df[
            'function'].unique()
        for function in functions_to_process:
            self.save_test_data_for_function(function)
        self.save_test_data()
