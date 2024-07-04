import os

import matplotlib.pyplot as plt

from FitnessDataAnalyzer import FitnessDataAnalyzer


def main():
    # Der relative Pfad vom aktuellen Arbeitsverzeichnis zu 'test_mutation_rate' im 'log' Ordner
    base_dir = os.path.join('..', 'log', 'test_mutation_rate')

    # Beispiel der Nutzung:
    analyzer = FitnessDataAnalyzer(base_dir, max_generations=10000)
    analyzer2 = FitnessDataAnalyzer(base_dir, max_generations=500000)


    # # Statistiken berechnen und ausgeben
    # stats = analyzer.calculate_statistics()
    # print("Statistiken für alle Parameter:")
    # for param, stat in stats.items():
    #     print(f"{param}: Mean={stat['mean']}, Std={stat['std']}, Min={stat['min']}, Max={stat['max']}")

    # Durchschnittliche Fitnessverläufe für alle Parameter plotten
    # analyzer.plot_average_fitness()

    # analyzer.plot_violin()
    #
    analyzer.plot_boxplot()
    analyzer2.plot_boxplot()
    #
    # analyzer.plot_heatmap()
    #
    # analyzer.perform_anova()
    #
    # analyzer.perform_tukey_test()
    #
    # analyzer.perform_mannwhitneyu_test("0.01", "0.05")

    # analyzer.plot_all()

    plt.show()


if __name__ == '__main__':
    main()
