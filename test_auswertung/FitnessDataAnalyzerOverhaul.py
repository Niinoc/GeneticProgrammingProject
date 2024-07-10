import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Function to process the directory and read fitness data into DataFrames
class FitnessDataAnalyzerOverhaul:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.test_name = self._get_test_name()
        self.df, self.average_df = self._process_directory()

    def _process_directory(self):
        df_list = []
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
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

        return pd.concat(df_list, ignore_index=True), \
        pd.concat(df_list, ignore_index=True).groupby(['function', 'parameter', 'generation'])[
            'fitness'].mean().reset_index()

    def _get_test_name(self):
        # Extrahieren des Testordnernamens ohne das Präfix 'test_'
        return os.path.basename(self.root_dir).replace('test_', '')

    def plot_boxplot(self, function):
        subset = self.df[self.df['function'] == function]
        plt.figure(figsize=(15, 10))
        sns.boxplot(x='parameter', y='fitness', data=subset)
        plt.title(f'Fitness Distribution per {self.test_name}')
        plt.xlabel('Parameter')
        plt.ylabel('Fitness (MSE)')
        plt.grid(True)

    def plot_heatmap(self, function):
        subset = self.df[self.df['function'] == function]
        plt.figure(figsize=(15, 10))
        sns.heatmap(subset, cmap="viridis")
        plt.title(f'Heatmap of Fitness (MSE) over Generations for {self.test_name}')
        plt.xlabel('Generation')
        plt.ylabel('Parameter')

    def plot_violin(self, function):
        subset = self.df[self.df['function'] == function]
        plt.figure(figsize=(15, 10))
        sns.violinplot(x='Parameter', y='FitnessMSE', data=subset)
        plt.title(f'Violin Plot of Fitness (MSE) per {self.test_name}')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')

    def plot_fitness_for_multiple_parameters(self, function):
        subset = self.average_df[self.average_df['function'] == function]
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=subset, x='generation', y='fitness', hue='parameter')
        plt.title(f'Fitness Trajectories for Multiple Parameters of {function}')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend(title='Parameter')

    def plot_fitness_for_multiple_functions(self, parameter):
        subset = self.average_df[self.average_df['parameter'] == parameter]
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=subset, x='generation', y='fitness', hue='function')
        plt.title(f'Fitness Trajectories for Multiple Functions of Parameter {parameter}')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend(title='Function')
