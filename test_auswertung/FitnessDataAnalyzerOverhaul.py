import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import sympy as sp


class FitnessDataAnalyzerOverhaul:
    def __init__(self, root_dir, plot_dir_name, allowed_functions=None, allowed_params=None):
        self.root_dir = root_dir
        self.plot_dir_name = plot_dir_name
        self.allowed_functions = allowed_functions
        self.allowed_params = allowed_params
        
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
            temp_df, final_function, good_fitness = self._process_best_fitness(root, files, function_dir, param_dir, seed_dir)
            
            if temp_df is not None:
                df_list.append(temp_df)

            # Extract diversity data
            start_diversity = self._extract_diversity(root, files, 'initialpopulation', good_fitness)
            end_diversity = self._extract_diversity(root, files, 'finalpopulation', good_fitness)

            # Compile test data if all conditions are met
            if good_fitness and final_function is not None:
                test_data.append([function_dir, param_dir, seed_dir, final_function, 
                                f"{round(float(start_diversity), 2)} ",
                                f"{round(float(end_diversity), 2)} "]) 

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
            function_dir, param_dir, seed_dir = relative_path.split(os.sep)
            
            # Überprüfen, ob die Funktion in der Liste der erlaubten Funktionen enthalten ist
            if self.allowed_functions is not None and function_dir not in self.allowed_functions:
                return None, None, None
        
            # Überprüfen, ob der Parameter in der Liste der erlaubten Parameter enthalten ist
            if self.allowed_params is not None and param_dir not in self.allowed_params:
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
            temp_df = pd.read_csv(file_path)
            
            temp_df['function'] = function_dir
            temp_df['parameter'] = param_dir
            temp_df['seed'] = seed_dir
            temp_df.rename(columns={'FitnessMSE': 'fitness'}, inplace=True)

            good_fitness = temp_df['fitness'].iloc[-1] < 1e-11
            final_function = None

            if good_fitness:
                final_function = self._simplify_final_function(root)

            return temp_df, final_function, good_fitness
        return None, None, False
    
    def _simplify_final_function(self, root):
        finalbehavior_path = os.path.join(root, 'out.finalbehavior.txt')
        if os.path.exists(finalbehavior_path):
            with open(finalbehavior_path, 'r') as f:
                first_line = f.readline().strip()
                if '# final function: ' in first_line:
                    final_function = first_line.split('# final function: ')[1]
                    sympy_expr = sp.sympify(final_function)
                    return sp.simplify(sympy_expr)
        return None

    def _extract_diversity(self, root, files, population_type, good_fitness):
        diversity = 'notfound'
        if good_fitness and f'out.{population_type}.txt' in files:
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


    def _compile_final_data(self, df_list, test_data):
        test_data_df = pd.DataFrame(test_data, columns=['function_dir', 'param_dir', 'seed_dir', 'final_function',
                                                        'start_diversity', 'end_diversity'])
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
        functions_to_process = self.allowed_functions if self.allowed_functions is not None else self.df['function'].unique()
        for function in functions_to_process:
            self.plot_fitness_for_multiple_parameters(function)
            plt.close()
            self.plot_boxplot(function)
            plt.close()
            self.plot_heatmap(function)
            plt.close()
            self.plot_violin(function)
            plt.close()
            
    def save_all_test_data(self):
        functions_to_process = self.allowed_functions if self.allowed_functions is not None else self.df['function'].unique()
        for function in functions_to_process:
            self.save_test_data_for_function(function)
