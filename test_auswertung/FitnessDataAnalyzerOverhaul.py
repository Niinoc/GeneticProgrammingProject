import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import sympy as sp


class FitnessDataAnalyzerOverhaul:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.test_name = self._get_test_name()
        self.df, self.average_df, self.final_functions_df = self._process_directory()
        self.function_subsets = {}
        self.function_average_subsets = {}
        self.parameter_average_subsets = {}
        self._initialize_subsets()

    def _process_directory(self):
        df_list = []
        final_functions_data = []
        files_to_delete = [
            'out.initialbehavior.txt',
            'out.initialpopulation.txt',
            'out.finalpopulation.txt',
            'out.fitnessFunction.txt'
        ]
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file in files_to_delete:
                    os.remove(os.path.join(root, file))
                if file == 'out.bestfitness.txt':
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, self.root_dir)

                    try:
                        function_dir, param_dir, seed_dir = relative_path.split(os.sep)
                    except ValueError:
                        print(f"Skipping invalid directory structure: {relative_path}")
                        continue

                    temp_df = pd.read_csv(file_path)

                    # Append each row to the main DataFrame
                    temp_df['function'] = function_dir
                    temp_df['parameter'] = param_dir
                    temp_df['seed'] = seed_dir
                    temp_df.rename(columns={'FitnessMSE': 'fitness'}, inplace=True)

                    df_list.append(temp_df)

                    if temp_df['fitness'].iloc[-1] < 1e-12:
                        finalbehavior_path = os.path.join(root, 'out.finalbehavior.txt')
                        if os.path.exists(finalbehavior_path):
                            with open(finalbehavior_path, 'r') as f:
                                first_line = f.readline().strip()
                                if '# final function: ' in first_line:
                                    final_function = first_line.split('# final function: ')[1]
                                    sympy_expr = sp.sympify(final_function)
                                    simplified_expr = sp.simplify(sympy_expr)
                                    final_functions_data.append([function_dir, simplified_expr])

        final_functions_df = pd.DataFrame(final_functions_data, columns=['function_dir', 'final_function'])

        return pd.concat(df_list, ignore_index=True), \
            pd.concat(df_list, ignore_index=True).groupby(['function', 'parameter', 'generation'])[
                'fitness'].mean().reset_index(), final_functions_df

    def _get_test_name(self):
        # extract testname without prefix 'test_'
        return os.path.basename(self.root_dir).replace('test_', '')

    def _initialize_subsets(self):
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

    def _save_plot(self, plt, function, plot_type):
        output_dir = os.path.join(self.root_dir, function)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print("Speicherort existierte nicht")
        if plot_type == 'heatmap' or plot_type == 'boxplot':
            plot_path = os.path.join(output_dir, f'{function}_{plot_type}.png')
            plt.savefig(plot_path, format='png', dpi=500)
        else:
            plot_path = os.path.join(output_dir, f'{function}_{plot_type}.svg')
            plt.savefig(plot_path, format='svg', dpi=300)

    def save_functions(self):
        for row in self.final_functions_df[['function_dir', 'final_function']].itertuples(index=False):
            function_dir, final_function = row

            output_dir = os.path.join(self.root_dir, function_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Speicherort existierte nicht: {output_dir}")

            final_functions_path = os.path.join(output_dir, 'finalFunctions.txt')
            with open(final_functions_path, 'a') as file:
                file.write(str(final_function) + '\n')

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

    def plot_all(self, functions):
        for function in functions:
            self.plot_fitness_for_multiple_parameters(function)
            plt.close()
            self.plot_boxplot(function)
            plt.close()
            self.plot_heatmap(function)
            plt.close()
            self.plot_violin(function)
            plt.close()
