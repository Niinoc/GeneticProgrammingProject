import os
import random

from FitnessDataAnalyzerOverhaul import FitnessDataAnalyzerOverhaul


def main():
    base_dir = os.path.join('..', 'log', 'test_mutation_rate_new_analyzer_test')
    # Name des Ordners in den gespeichert werden soll
    plot_dir_name = "auswertung_alles"
    # Funktionen welche berücksichtigt werden sollen, wenn None -> alle
    functions = None
    # ['I.8.14', 'I.11.19', 'I.27.6', 'I.29.4', 'I.39.1', 'I.50.26', 'II.3.24', 'II.11.28', 'II.38.14']
    # Parameterwerte welche berücksichtigt werden sollen, wenn None -> alle
    parameters = None
    # seeds = pick_seeds(10)
    # seeds = ['seed_1', 'seed_2', 'seed_3']
    seeds = None
    # print(seeds)
    analyzer = FitnessDataAnalyzerOverhaul(base_dir, plot_dir_name, functions, parameters, seeds)

    print(analyzer.df)
    print(analyzer.average_df)

    analyzer.save_all_test_data()
    analyzer.save_all_plots()

    # nur mit 2 parametern und sehr wenigen runs oder mit einem parameter verwenden
    # -> zB functions=None, parameters=['0.09'], seeds=['seed_1','seed_2','seed_3','seed_4','seed_5']
    # analyzer.save_individual_fitness_plot()


def pick_seeds(anzahl):
    return [f'seed_{num}' for num in random.sample(range(1, 50 + 1), anzahl)]


if __name__ == '__main__':
    main()
