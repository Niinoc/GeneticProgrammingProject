import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import sympy as sp


class FitnessDataAnalyzerOverhaul:
    def __init__(self, root_dir, plot_dir_name, allowed_functions=None, allowed_params=None, allowed_seeds=None):
        self.root_dir = root_dir
        self.plot_dir_name = plot_dir_name
        self.allowed_functions = allowed_functions
        self.allowed_params = allowed_params
        self.allowed_seeds = allowed_seeds

        self.test_name = self._get_test_name()
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

        files_to_delete = [
            # 'out.initialbehavior.txt',
            # 'out.fitnessFunction.txt'
        ]

        for root, dirs, files in os.walk(self.root_dir):
            # Initialize directory-related variables before processing files
            function_dir, param_dir, seed_dir = self._extract_directory_info(root)

            if function_dir is None:
                continue  # Skip if the directory structure is invalid

            # Display progress by printing the current function_dir if it has changed
            if function_dir != last_dir:
                last_dir = function_dir
                print(f"Processing directory: {last_dir}")

            # Delete unnecessary files
            self._delete_unnecessary_files(root, files, files_to_delete)

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

    def _get_test_name(self):
        # extract testname without prefix 'test_'
        return os.path.basename(self.root_dir).replace('test_', '')

    def _delete_unnecessary_files(self, root, files, files_to_delete):
        for file in files:
            if file in files_to_delete:
                os.remove(os.path.join(root, file))

    def _extract_directory_info(self, root):
        relative_path = os.path.relpath(root, self.root_dir)
        try:
            parts = relative_path.split(os.sep)
            # print(f"Relative Path: {relative_path}")
            if len(parts) < 3:
                # print(f"Skipping invalid directory structure: {relative_path}")
                return None, None, None

            function_dir, param_dir, seed_dir = parts[-3], parts[-2], parts[-1]

            # print(f"Extracted: function_dir={function_dir}, param_dir={param_dir}, seed_dir={seed_dir}")

            # Überprüfen, ob die Funktion in der Liste der erlaubten Funktionen enthalten ist
            if self.allowed_functions is not None and function_dir not in self.allowed_functions:
                # print(f"Function {function_dir} not allowed")
                return None, None, None

            # Überprüfen, ob der Parameter in der Liste der erlaubten Parameter enthalten ist
            if self.allowed_params is not None and param_dir not in self.allowed_params:
                # print(f"Parameter {param_dir} not allowed")
                return None, None, None

            if self.allowed_seeds is not None and seed_dir not in self.allowed_seeds:
                # print(f"Seed {seed_dir} not allowed")
                return None, None, None

            return function_dir, param_dir, seed_dir
        except ValueError:
            # print(f"Skipping invalid directory structure: {relative_path}")
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

    def _get_output_dir(self, function_dir):
        output_dir = os.path.join(self.root_dir, function_dir, self.plot_dir_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _save_plot(self, plt, function, plot_type):
        output_dir = self._get_output_dir(function)

        if plot_type in ['heatmap', 'boxplot']:
            file_extension, dpi_value = 'png', 500
        else:
            file_extension, dpi_value = 'svg', 300
        plot_path = os.path.join(output_dir, f'{function}_{plot_type}.{file_extension}')
        plt.savefig(plot_path, format=file_extension, dpi=dpi_value)

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

    def plot_boxplot(self, function):
        print(f'boxplot {function}')
        subset = self.function_subsets[function]
        plt.figure(figsize=(15, 10))
        sns.boxplot(x='parameter', y='fitness', data=subset, order=subset['parameter'].cat.categories)
        plt.title(f'Fitness Distribution of {function} per {self.test_name}')
        plt.xlabel('Parameter')
        plt.ylabel('Fitness (MSE)')
        plt.grid(True)
        self._save_plot(plt, function, 'boxplot')

    def plot_heatmap(self, function):
        print(f'heatmap {function}')
        subset = self.function_subsets[function]
        # Pivot the table to get a matrix format for the heatmap
        heatmap_data = subset.pivot_table(index='parameter', columns='generation', values='fitness', observed=False)
        heatmap_data = heatmap_data.sort_index(level='parameter')
        plt.figure(figsize=(15, 10))
        sns.heatmap(heatmap_data, cmap="viridis")
        plt.title(f'Heatmap of Fitness (MSE) over Generations for {function} per {self.test_name}')
        plt.xlabel('Generation')
        plt.ylabel('Parameter')
        self._save_plot(plt, function, 'heatmap')

    def plot_violin(self, function):
        print(f'violin {function}')
        subset = self.function_subsets[function]
        plt.figure(figsize=(15, 10))
        sns.violinplot(x='parameter', y='fitness', data=subset, cut=0, density_norm='width',
                       order=subset['parameter'].cat.categories)
        plt.title(f'Violin Plot of {function} per {self.test_name}')
        plt.xlabel('Parameter')
        plt.ylabel('Fitness (MSE)')
        self._save_plot(plt, function, 'violinplot')

    def plot_fitness_for_multiple_parameters(self, function):
        print(f'avg_fitness {function}')
        subset = self.function_average_subsets[function]
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=subset, x='generation', y='fitness', hue='parameter')
        plt.title(f'Fitness Trajectories of {function} for Multiple Parameters per {self.test_name}')
        plt.yscale('log')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend(title='Parameter')
        self._save_plot(plt, function, 'average_fitness')

    def plot_fitness_for_multiple_parameters_scaled(self, function):
        print(f'avg_fitness {function}')
        subset = self.function_average_subsets[function]

        # Finde den kleinsten Parameterwert
        min_param = subset['parameter'].astype(float).min()
        median_param = subset['parameter'].astype(float).median()

        # Finde die maximale Generation
        max_generation = subset['generation'].max()

        # Neue Spalte für skalierte maximale Generationen
        subset['scaled_max_generation'] = subset['parameter'].astype(float).apply(
            lambda x: max_generation * (min_param / x)
        )

        # Ausgabe der berechneten maximalen Generationen für jeden Parameter
        for param in subset['parameter'].unique():
            max_gen = subset[subset['parameter'] == param]['scaled_max_generation'].iloc[0]

        # Berechnung des prozentualen Fortschritts auf Basis der skalierten maximalen Generationen
        subset['progress'] = subset['generation'] / subset['scaled_max_generation']

        plt.figure(figsize=(12, 8))

        # Für jeden Parameter einen eigenen Plot mit einer eigenen Farbe
        colors = sns.color_palette("husl", len(subset['parameter'].unique()))

        for i, (param, group) in enumerate(subset.groupby('parameter', observed=True)):
            # Filterung der Daten, um nur bis zur berechneten maximalen Generation zu plotten
            max_gen_for_param = group['scaled_max_generation'].iloc[0]
            filtered_group = group[group['generation'] <= max_gen_for_param]

            # Hinzufügen der Generationsgrenze zur Legende
            sns.lineplot(data=filtered_group, x='progress', y='fitness', color=colors[i],
                         label=f'Param {param} (Max Gen: {max_gen_for_param:.0f})')

        plt.title(
            f'Fitness Trajectories of {function} for Multiple Parameters (Scaled by Progress) per {self.test_name}')
        plt.yscale('log')
        plt.xlabel('Progress (%)')
        plt.ylabel('Fitness')
        plt.legend(title='Parameter')
        self._save_plot(plt, function, 'average_fitness_scaled')

    def plot_individual_fitness_for_multiple_parameters(self, function):
        print(f'individual_fitness {function}')
        subset = self.function_subsets[function]
        plt.figure(figsize=(12, 8))
        if len(self.allowed_seeds) > 10:
            sns.lineplot(data=subset, x='generation', y='fitness', hue='seed', legend=False)
        elif len(self.allowed_params) > 10:
            sns.lineplot(data=subset, x='generation', y='fitness', hue='seed', style='parameter', legend=False)
        else:
            sns.lineplot(data=subset, x='generation', y='fitness', hue='seed', style='parameter')
            plt.legend(title='Parameter / Seed')

        plt.title(f'Fitness Trajectories of {function} for Multiple Runs and Parameters per {self.test_name}')
        plt.yscale('log')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        self._save_plot(plt, function, 'individual_fitness')

    def plot_fitness_for_multiple_functions(self, parameter):
        print(f'avg_fitness {parameter}')
        subset = self.parameter_average_subsets[parameter]
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=subset, x='generation', y='fitness', hue='function')
        plt.title(f'Fitness Trajectories for Multiple Functions of Parameter {parameter} per {self.test_name}')
        plt.yscale('log')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend(title='Function')

    def save_all_plots(self):
        functions_to_process = self.allowed_functions if self.allowed_functions is not None else self.df[
            'function'].unique()
        for function in functions_to_process:
            self.plot_fitness_for_multiple_parameters(function)
            plt.close()
            self.plot_fitness_for_multiple_parameters_scaled(function)
            plt.close()

            # self.plot_boxplot(function)
            # plt.close()
            # self.plot_heatmap(function)
            # plt.close()
            # self.plot_violin(function)
            # plt.close()

    def save_individual_fitness_plot(self):
        functions_to_prozess = self.allowed_functions if self.allowed_functions is not None else self.df[
            'function'].unique()
        for function in functions_to_prozess:
            self.plot_individual_fitness_for_multiple_parameters(function)
            plt.close()

    def save_all_test_data(self):
        functions_to_process = self.allowed_functions if self.allowed_functions is not None else self.df[
            'function'].unique()
        for function in functions_to_process:
            self.save_test_data_for_function(function)
        self.save_test_data()
