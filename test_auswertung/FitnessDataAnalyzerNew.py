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
        # Extract the test folder name without the 'test_' prefix
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
                        data[param_dir][seed_dir] = {}
                        for function_dir in os.listdir(seed_path):
                            function_path = os.path.join(seed_path, function_dir)
                            if os.path.isdir(function_path):
                                txt_file_path = os.path.join(function_path, "out.bestfitness.txt")
                                if os.path.isfile(txt_file_path):
                                    df = pd.read_csv(txt_file_path, sep=",")
                                    if self.max_generations is not None:
                                        df = df[df['generation'] <= self.max_generations]
                                    data[param_dir][seed_dir][function_dir] = df
        return data

    def get_data_for_parameter(self, parameter):
        return self.data.get(parameter, {})

    def calculate_average_fitness(self, parameter, functions=None, max_generations=None):
        data_for_param = self.get_data_for_parameter(parameter)
        if not data_for_param:
            print(f"No data found for parameter: {parameter}")
            return None

        fitness_data = []
        for seed, func_dict in data_for_param.items():
            for func_dir, df in func_dict.items():
                if (functions is None or func_dir in functions) and (max_generations is None or df['generation'].max() <= max_generations):
                    fitness_data.append(df[df['generation'] <= max_generations]["FitnessMSE"].values if max_generations else df["FitnessMSE"].values)

        if not fitness_data:
            print(f"No data found for parameter: {parameter} with specified functions and generations")
            return None

        fitness_df = pd.DataFrame(fitness_data)
        average_fitness = fitness_df.mean(axis=0)
        return average_fitness


    def calculate_statistics(self, function=None):
        stats = {}
        for parameter in self.data.keys():
            data_for_param = self.get_data_for_parameter(parameter)
            fitness_values = []
            for seed, functions in data_for_param.items():
                for func_dir, df in functions.items():
                    if function is None or function == func_dir:
                        fitness_values.extend(df["FitnessMSE"].values)

            if fitness_values:
                stats[parameter] = {
                    "mean": pd.Series(fitness_values).mean(),
                    "std": pd.Series(fitness_values).std(),
                    "min": pd.Series(fitness_values).min(),
                    "max": pd.Series(fitness_values).max()
                }
        return stats

    def plot_average_fitness(self, functions=None, max_generations=None):
        plt.figure(figsize=(10, 6))
        
        for parameter in self.data.keys():
            average_fitness = self.calculate_average_fitness(parameter, functions, max_generations)
            if average_fitness is not None:
                plt.plot(average_fitness, label=f'{parameter}')

        plt.xlabel('Generation')
        plt.ylabel('Average Fitness (MSE)')
        plt.title(f'Average Fitness per Generation for Different {self.test_name}s')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_heatmap(self, functions=None, max_generations=None):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for seed, func_dict in seed_dict.items() for func, df in func_dict.items() if (functions is None or func in functions) and (max_generations is None or df['generation'].max() <= max_generations)]
        )
        if max_generations is not None:
            combined_data = combined_data[combined_data['generation'] <= max_generations]
        data_pivot = combined_data.pivot_table(index='Parameter', columns='generation', values='FitnessMSE')
        sns.heatmap(data_pivot, cmap="viridis")
        plt.title(f'Heatmap of Fitness (MSE) over Generations for {self.test_name}')
        plt.xlabel('Generation')
        plt.ylabel('Parameter')
        plt.show()

    def plot_violin(self, functions=None, max_generations=None):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for seed, func_dict in seed_dict.items() for func, df in func_dict.items() if (functions is None or func in functions) and (max_generations is None or df['generation'].max() <= max_generations)]
        )
        if max_generations is not None:
            combined_data = combined_data[combined_data['generation'] <= max_generations]
        sns.violinplot(x='Parameter', y='FitnessMSE', data=combined_data)
        plt.title(f'Violin Plot of Fitness (MSE) per {self.test_name}')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.show()

    def plot_boxplot(self, functions=None, max_generations=None):
        plt.figure(figsize=(15, 10))
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for seed, func_dict in seed_dict.items() for func, df in func_dict.items() if (functions is None or func in functions) and (max_generations is None or df['generation'].max() <= max_generations)]
        )
        if max_generations is not None:
            combined_data = combined_data[combined_data['generation'] <= max_generations]
        sns.boxplot(x='Parameter', y='FitnessMSE', data=combined_data)
        plt.title(f'Fitness Distribution per {self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.grid(True)
        plt.show()


    def plot_all(self):
        self.plot_average_fitness()
        self.plot_boxplot()
        self.plot_heatmap()
        self.plot_violin()

    def perform_anova(self):
        groups = [df['FitnessMSE'].values for param_dict in self.data.values() for seed_dict in param_dict.values() for df in seed_dict.values()]
        f_val, p_val = stats.f_oneway(*groups)
        print(f"F-value: {f_val}, P-value: {p_val}")

    def perform_tukey_test(self):
        combined_data = pd.concat(
            [df.assign(Parameter=param) for param, seed_dict in self.data.items() for seed, func_dict in seed_dict.items() for df in func_dict.values()])
        tukey = pairwise_tukeyhsd(combined_data['FitnessMSE'], combined_data['Parameter'])
        print(tukey)

    def perform_mannwhitneyu_test(self, parameter1, parameter2):
        available_parameters = list(self.data.keys())
        if parameter1 not in self.data:
            print(f"Parameter {parameter1} not found in the data. Available parameters: {available_parameters}")
            return
        if parameter2 not in self.data:
            print(f"Parameter {parameter2} not found in the data. Available parameters: {available_parameters}")
            return

        data1 = pd.concat([df for seed_dict in self.data[parameter1].values() for df in seed_dict.values()])
        data2 = pd.concat([df for seed_dict in self.data[parameter2].values() for df in seed_dict.values()])
        u_stat, p_val = stats.mannwhitneyu(data1['FitnessMSE'], data2['FitnessMSE'])
        print(f"U-statistic: {u_stat}, P-value: {p_val}")
