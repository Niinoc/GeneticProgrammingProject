class FitnessDataAnalyzer:
    def __init__(self, excel_file, max_generations=None):
        self.excel_file = excel_file
        self.test_name = self._get_test_name()
        self.max_generations = max_generations
        self.data = self._load_data()

    def _get_test_name(self):
        # Extract the test name from the Excel file name
        return os.path.basename(self.excel_file).replace('fitness_data_', '').replace('.xlsx', '')

    def _load_data(self):
        df = pd.read_excel(self.excel_file)
        if self.max_generations is not None:
            df = df[df['Generation'] <= self.max_generations]
        return df

    def get_data_for_parameter(self, parameter):
        return self.data[self.data['Parameter'] == parameter]

    def calculate_average_fitness(self, parameter, functions=None, max_generations=None):
        filtered_df = self.get_data_for_parameter(parameter)
        
        if functions is not None:
            filtered_df = filtered_df[filtered_df['Function'].isin(functions)]
        
        if max_generations is not None:
            filtered_df = filtered_df[filtered_df['Generation'] <= max_generations]

        if filtered_df.empty:
            print(f"No data found for parameter: {parameter} with specified functions and generations")
            return None

        average_fitness = filtered_df.groupby('Generation')['FitnessMSE'].mean()
        return average_fitness

    def calculate_statistics(self, function=None):
        stats = {}
        for parameter in self.data['Parameter'].unique():
            filtered_df = self.get_data_for_parameter(parameter)
            
            if function:
                filtered_df = filtered_df[filtered_df['Function'] == function]

            fitness_values = filtered_df['FitnessMSE'].values
            if len(fitness_values) > 0:
                stats[parameter] = {
                    "mean": pd.Series(fitness_values).mean(),
                    "std": pd.Series(fitness_values).std(),
                    "min": pd.Series(fitness_values).min(),
                    "max": pd.Series(fitness_values).max()
                }
        return stats

    def plot_average_fitness(self, functions=None, max_generations=None):
        plt.figure(figsize=(10, 6))
        
        for parameter in self.data['Parameter'].unique():
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
        filtered_data = self.data.copy()
        
        if functions is not None:
            filtered_data = filtered_data[filtered_data['Function'].isin(functions)]
        
        if max_generations is not None:
            filtered_data = filtered_data[filtered_data['Generation'] <= max_generations]

        data_pivot = filtered_data.pivot_table(index='Parameter', columns='Generation', values='FitnessMSE')
        sns.heatmap(data_pivot, cmap="viridis")
        plt.title(f'Heatmap of Fitness (MSE) over Generations for {self.test_name}')
        plt.xlabel('Generation')
        plt.ylabel('Parameter')
        plt.show()

    def plot_violin(self, functions=None, max_generations=None):
        plt.figure(figsize=(15, 10))
        filtered_data = self.data.copy()
        
        if functions is not None:
            filtered_data = filtered_data[filtered_data['Function'].isin(functions)]
        
        if max_generations is not None:
            filtered_data = filtered_data[filtered_data['Generation'] <= max_generations]

        sns.violinplot(x='Parameter', y='FitnessMSE', data=filtered_data)
        plt.title(f'Violin Plot of Fitness (MSE) per {self.test_name}')
        plt.xlabel(f'{self.test_name}')
        plt.ylabel('Fitness (MSE)')
        plt.show()

    def plot_boxplot(self, functions=None, max_generations=None):
        plt.figure(figsize=(15, 10))
        filtered_data = self.data.copy()
        
        if functions is not None:
            filtered_data = filtered_data[filtered_data['Function'].isin(functions)]
        
        if max_generations is not None:
            filtered_data = filtered_data[filtered_data['Generation'] <= max_generations]

        sns.boxplot(x='Parameter', y='FitnessMSE', data=filtered_data)
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
        groups = [df['FitnessMSE'].values for df in self.data.groupby('Parameter')]
        f_val, p_val = stats.f_oneway(*groups)
        print(f"F-value: {f_val}, P-value: {p_val}")

    def perform_tukey_test(self):
        tukey = pairwise_tukeyhsd(self.data['FitnessMSE'], self.data['Parameter'])
        print(tukey)

    def perform_mannwhitneyu_test(self, parameter1, parameter2):
        available_parameters = self.data['Parameter'].unique()
        if parameter1 not in available_parameters:
            print(f"Parameter {parameter1} not found in the data. Available parameters: {available_parameters}")
            return
        if parameter2 not in available_parameters:
            print(f"Parameter {parameter2} not found in the data. Available parameters: {available_parameters}")
            return

        data1 = self.data[self.data['Parameter'] == parameter1]['FitnessMSE']
        data2 = self.data[self.data['Parameter'] == parameter2]['FitnessMSE']
        u_stat, p_val = stats.mannwhitneyu(data1, data2)
        print(f"U-statistic: {u_stat}, P-value: {p_val}")
