import os

from FitnessDataAnalyzerOverhaul import FitnessDataAnalyzerOverhaul


def main():
    # Der relative Pfad vom aktuellen Arbeitsverzeichnis zu 'test_mutation_rate' im 'log' Ordner
    base_dir = os.path.join('..', 'log', 'test_mutation_rate')
    analyzer = FitnessDataAnalyzerOverhaul(base_dir)
    print(analyzer.df)
    print(analyzer.average_df)

    functions = ['I.8.14', 'I.11.19', 'I.27.6', 'I.29.4', 'I.39.1', 'I.50.26', 'II.3.24', 'II.11.28', 'II.38.14']
    functions2 = ['I.27.6']

    analyzer.plot_all(functions2)

if __name__ == '__main__':
    
    
    main()
    
