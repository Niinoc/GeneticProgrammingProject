import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class FitnessDataAnalyzer:
    def __init__(self, base_dir, max_generations=None):
        self.base_dir = base_dir
        self.test_name = self._get_test_name()
        self.max_generations = max_generations
        self.data = self._load_data()

    def _get_test_name(self):
        # Extrahieren des Testordnernamens ohne das Präfix 'test_'
        return os.path.basename(self.base_dir).replace('test_', '')

    def _load_data(self):
        data = {}
        for param_dir in os.listdir(self.base_dir):
            param_path = os.path.join(self.base_dir, param_dir)
            if os.path.isdir(param_path):
                data[param_dir] = {}
                for seed_dir in os.listdir(param_path):
                    seed_path = os.path.join(param_path, seed_dir)
                    if os.path.isdir(seed_path):
                        txt_file_path = os.path.join(seed_path, "out.bestfitness.txt")
                        if os.path.isfile(txt_file_path):
                            df = pd.read_csv(txt_file_path, sep=",")
                            if self.max_generations is not None:
                                df = df[df['generation'] <= self.max_generations]
                            data[param_dir][seed_dir] = df
        return data

    def get_data_for_parameter(self, parameter):
        return self.data.get(parameter, {})

    def calculate_average_fitness(self, parameter):
        data_for_param = self.get_data_for_parameter(parameter)
        if not data_for_param:
            print(f"No data found for parameter: {parameter}")
            return None

        fitness_data = []
        for seed, df in data_for_param.items():
            fitness_data.append(df["FitnessMSE"].values)

        fitness_df = pd.DataFrame(fitness_data)
        average_fitness = fitness_df.mean(axis=0)
        return average_fitness

    def calculate_statistics(self):
        stats = {}
        for parameter in self.data.keys():
            data_for_param = self.get_data_for_parameter(parameter)
            fitness_values = []
            for seed, df in data_for_param.items():
                fitness_values.extend(df["FitnessMSE"].values)
            stats[parameter] = {
                "mean": pd.Series(fitness_values).mean(),
                "std": pd.Series(fitness_values).std(),
                "min": pd.Series(fitness_values).min(),
                "max": pd.Series(fitness_values).max()
            }
        return stats

    def plot_average_fitness(self):
        plt.figure(figsize=(10, 6))
        for parameter in self.data.keys():
            average_fitness = self.calculate_average_fitness(parameter)
            if average_fitness is not None:
                plt.plot(average_fitness, label=f'{parameter}')

        plt.xlabel('Generation')
        plt.ylabel('Average Fitness (MSE)')
        plt.title(f'Average Fitness per Generation for Different {self.test_name}s')
        plt.legend()
        plt.grid(True)

    def plot_heatmap(self):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for df in seed_dict.values()])
        data_pivot = combined_data.pivot_table(index='Parameter', columns='generation', values='FitnessMSE')
        sns.heatmap(data_pivot, cmap="viridis")
        plt.title(f'Heatmap of Fitness (MSE) over Generations for {self.test_name}')
        plt.xlabel('Generation')
        plt.ylabel('Parameter')

    def plot_violin(self):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for df in seed_dict.values()])
        sns.violinplot(x='Parameter', y='FitnessMSE', data=combined_data)
        plt.title(f'Violin Plot of Fitness (MSE) per {self.test_name}')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')

    def plot_boxplot(self):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for df in seed_dict.values()])
        sns.boxplot(x='Parameter', y='FitnessMSE', data=combined_data)
        plt.title(f'Fitness Distribution per {self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.grid(True)

    def plot_all(self):
        self.plot_average_fitness()
        self.plot_boxplot()
        self.plot_heatmap()
        self.plot_violin()

    def perform_anova(self):
        groups = [fitness_df['FitnessMSE'].values for seeds in self.data.values() for fitness_df in seeds.values()]
        f_val, p_val = stats.f_oneway(*groups)
        print(f"F-value: {f_val}, P-value: {p_val}")

    def perform_tukey_test(self):
        df = pd.concat([df.assign(param=param) for param, seeds in self.data.items() for df in seeds.values()])
        tukey = pairwise_tukeyhsd(df['FitnessMSE'], df['param'])
        print(tukey)

    def perform_mannwhitneyu_test(self, parameter1, parameter2):
        available_parameters = list(self.data.keys())
        if parameter1 not in self.data:
            print(f"Parameter {parameter1} not found in the data. Available parameters: {available_parameters}")
            return
        if parameter2 not in self.data:
            print(f"Parameter {parameter2} not found in the data. Available parameters: {available_parameters}")
            return

        data1 = pd.concat([df for df in self.data[parameter1].values()])
        data2 = pd.concat([df for df in self.data[parameter2].values()])
        u_stat, p_val = stats.mannwhitneyu(data1['FitnessMSE'], data2['FitnessMSE'])
        print(f"U-statistic: {u_stat}, P-value: {p_val}")
