import os

from FitnessDataAnalyzerOverhaul import FitnessDataAnalyzerOverhaul


def main():

    base_dir = os.path.join('..', 'log', 'tests_with_old_operators', 'test_mutation_rate_very_fine')
    # Name des Ordners in den gespeichert werden soll
    plot_dir_name = "test"
    # Funktionen welche berücksichtigt werden sollen, wenn None -> alle
    functions = ['I.8.14', 'I.11.19', 'I.27.6', 'I.29.4', 'I.39.1', 'I.50.26', 'II.3.24', 'II.11.28', 'II.38.14']
    # Parameterwerte welche berücksichtigt werden sollen, wenn None -> alle
    parameters = None
    
    analyzer = FitnessDataAnalyzerOverhaul(base_dir, plot_dir_name, functions, parameters)
    
    print(analyzer.df)
    print(analyzer.average_df)

    analyzer.save_all_test_data()
    analyzer.save_all_plots()


if __name__ == '__main__':
    main()
