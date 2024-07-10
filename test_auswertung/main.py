import os

import matplotlib.pyplot as plt

from FitnessDataAnalyzer import FitnessDataAnalyzer
from FitnessDataAnalyzerOverhaul import FitnessDataAnalyzerOverhaul


def main():
    # Der relative Pfad vom aktuellen Arbeitsverzeichnis zu 'test_mutation_rate' im 'log' Ordner
    base_dir = os.path.join('..', 'log', 'test_mutation_rate')
    analyzer = FitnessDataAnalyzerOverhaul(base_dir)
    print(analyzer.df)
    print(analyzer.average_df)

    functions1 = ['I.8.14', 'I.11.19', 'I.27.6', 'I.29.4']
    functions2 = ['I.39.1', 'I.50.26', 'II.3.24', 'II.11.28', 'II.38.14']

    for function in functions1:
        analyzer.plot_fitness_for_multiple_parameters(function)
    plt.show()

    for function in functions2:
        analyzer.plot_fitness_for_multiple_parameters(function)
    plt.show()

    for function in functions1:
        analyzer.plot_boxplot(function)
    plt.show()

    for function in functions2:
        analyzer.plot_boxplot(function)
    plt.show()


if __name__ == '__main__':
    main()
