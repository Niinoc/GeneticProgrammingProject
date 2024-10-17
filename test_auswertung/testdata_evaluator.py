import pandas as pd
import ast
import os
import seaborn as sns
from matplotlib import pyplot as plt
from collections import Counter
import itertools
import re

import pandas as pd
import ast
import re

import pandas as pd
import ast
import re

def read_data(file_path):
    """
    Liest die Daten aus einer Datei ein und konvertiert bestimmte Spalten in Listen.
    Entfernt geschweifte Klammern, wenn sie vorhanden sind und konvertiert nur numerische Spalten zu float-Listen.
    """
    # Daten einlesen
    df = pd.read_csv(file_path, sep=';')  # Passen Sie den Separator an Ihre Datei an

    # Spalten, die Listen enthalten
    list_columns = [
        'good_fitness', 'function_dir', 'final_function', 'final_fitness',
        'stagnation', 'start_diversity', 'end_diversity', 'found_generation'
    ]

    # Spalten, die numerische Listen enthalten, die zu floats konvertiert werden sollen
    numeric_list_columns = ['final_fitness', 'start_diversity', 'end_diversity', 'found_generation', 'stagnation']

    # Konvertiert die Spalten, die Listen enthalten, von Strings zu tatsächlichen Listen
    for col in list_columns:
        if col in df.columns:
            def safe_literal_eval(x):
                if isinstance(x, str) and x.strip() != '':
                    try:
                        # Entferne geschweifte Klammern, falls vorhanden
                        x = re.sub(r'[{}]', '', x)

                        # Ersetze 'nan' als eigenständiges Element durch 'None' mit Regex
                        x = re.sub(r'\bnan\b', 'None', x)

                        parsed_value = ast.literal_eval(x)

                        # Falls die Spalte numerisch sein sollte, konvertiere die Elemente zu float
                        if col in numeric_list_columns and isinstance(parsed_value, list):
                            return [float(item) if item is not None else None for item in parsed_value]

                        return parsed_value

                    except Exception as e:
                        print(f"Fehler beim Parsen von Spalte '{col}', Wert: {x}")
                        raise e
                else:
                    return []

            # Wende die Konvertierung auf die Spalte an
            df[col] = df[col].apply(safe_literal_eval)

    return df


def filter_data(df, condition):
    """
    Filtert die Daten basierend auf einer Bedingung.
    """
    filtered_df = df.query(condition)
    return filtered_df


def split_by_count_median(df, m):
    """
    Teilt die Daten in drei DataFrames auf:
    - 'better_df' enthält die Zeilen mit 'count' > (Median + m)
    - 'worse_df' enthält die Zeilen mit 'count' < (Median - m)
    - 'middle_df' enthält die Zeilen dazwischen
    """
    median_count = df['count'].median()
    better_df = df[df['count'] > (median_count + m)]
    worse_df = df[df['count'] < (median_count - m)]
    middle_df = df[(df['count'] >= (median_count - m)) & (df['count'] <= (median_count + m))]
    return better_df, worse_df, middle_df, median_count


def split_by_combined_score_with_relative_generation(df, lower_quantile=0.4, upper_quantile=0.6, count_weight=0.8,
                                                     generation_weight=0.2):
    """
    Teilt die Daten in drei DataFrames auf, basierend auf einer Kombination aus 'count' und der relativen 'mean_found_generation',
    wobei 'mean_found_generation' in Relation zur maximalen Anzahl der Generationen ('gen') gesetzt wird.

    Args:
    - df: Das Eingabedaten-Frame.
    - lower_quantile: Quantil für die untere Grenze (z.B. 0.2 für die schlechtesten 20 %).
    - upper_quantile: Quantil für die obere Grenze (z.B. 0.8 für die besten 20 %).
    - count_weight: Gewicht für die 'count'-Spalte im kombinierten Score (default: 0.5).
    - generation_weight: Gewicht für die relative 'mean_found_generation'-Spalte im kombinierten Score (default: 0.5).
    """
    # Berechne die relative Fundgeneration: mean_found_generation / gen
    df['relative_found_generation'] = df['mean_found_generation'] / df['gen']

    # Normiere 'count' und 'relative_found_generation'
    df['normalized_count'] = (df['count'] - df['count'].min()) / (df['count'].max() - df['count'].min())
    df['normalized_generation'] = (df['relative_found_generation'] - df['relative_found_generation'].min()) / (
            df['relative_found_generation'].max() - df['relative_found_generation'].min())

    # Kombiniere die beiden Spalten zu einem Score
    df['combined_score'] = (count_weight * df['normalized_count']) + (generation_weight * df['normalized_generation'])

    # Berechne Quantile basierend auf dem kombinierten Score
    lower_threshold = df['combined_score'].quantile(lower_quantile)
    upper_threshold = df['combined_score'].quantile(upper_quantile)
    median = df['combined_score'].median()

    # Split nach dem kombinierten Score (oberes und unteres Quantil)
    better_df = df[df['combined_score'] > upper_threshold]
    worse_df = df[df['combined_score'] < lower_threshold]

    # Sortiere nach 'combined_score', aufsteigend (kleinere Werte sind besser)
    better_df = better_df.sort_values(by=['combined_score'], ascending=True)
    worse_df = worse_df.sort_values(by=['combined_score'], ascending=True)

    return better_df, worse_df, lower_threshold, upper_threshold, median


def compute_solution_counts(better_df, param, solution_names):
    """
    Berechnet die absolute Häufigkeit jedes Lösungsnamens im 'better_df' für jeden Parameterwert.
    """
    data = []

    # Einzigartige Parameterwerte
    param_values = better_df[param].unique()

    for param_value in param_values:
        # Filtere 'better_df' für diesen Parameterwert
        df_param = better_df[better_df[param] == param_value]

        # Gesamtzahl der gefundenen Lösungen für diesen Parameterwert
        total_solutions = df_param['count'].sum()

        # Falls keine Lösungen gefunden wurden, überspringen
        if total_solutions == 0:
            continue

        # Initialisiere das Daten-Dictionary
        row = {'param_value': param_value}

        for solution_name in solution_names:
            col_name = f'count_{solution_name}'
            # Summe der Lösungsvorkommen
            total_solution_count = df_param[col_name].sum()
            # Speichern der absoluten Häufigkeit
            row[solution_name] = total_solution_count

        data.append(row)

    # Erstelle DataFrame
    counts_df = pd.DataFrame(data)
    counts_df.set_index('param_value', inplace=True)

    return counts_df


def analyze_hyperparameters(df_total, df_better, df_worse, save_dir):
    """
    Analysiert die Hyperparameter und erstellt Visualisierungen.
    """
    hyperparameters = ['regs', 'inst', 'popS', 'gen', 'mutInst', 'mutRegs', 'cross']

    # Ermittlung der Lösungsnamen
    solution_names = [col[len('count_'):] for col in df_total.columns if col.startswith('count_')]

    for param in hyperparameters:
        print(f"\nAnalyse des Hyperparameters '{param}':")

        # Daten für das Plotten vorbereiten
        summary_df, segments_df = prepare_summary_df(df_total, df_better, df_worse, param)

        # Berechnung der absoluten Häufigkeiten der Lösungsnamen
        counts_df = compute_solution_counts(df_better, param, solution_names)

        # Berechnung der statistischen Kennzahlen
        stats_df = compute_statistics(df_total, param)

        # Visualisierung
        plot_stacked_bars_with_lines((summary_df, segments_df), param, counts_df, save_dir, stats_df)


def process_additional_columns(df, top_n_solutions=None):
    """
    Verarbeitet die Spalten 'function_dir', 'start_diversity', 'end_diversity' und 'found_generation',
    und fügt neue Spalten zum DataFrame hinzu.

    - Berechnet Durchschnittswerte für 'start_diversity', 'end_diversity', 'found_generation'.
    - Erstellt neue Spalten für die häufigsten Lösungsnamen in 'function_dir'.
    """
    # Berechnung des Durchschnitts für die numerischen Spalten
    df['mean_start_diversity'] = df['start_diversity'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['mean_end_diversity'] = df['end_diversity'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['mean_found_generation'] = df['found_generation'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)

    # Ermittlung aller eindeutigen Werte in 'function_dir'
    all_function_dirs = [item for sublist in df['function_dir'] for item in sublist]
    function_counts = Counter(all_function_dirs)
    if top_n_solutions is not None:
        most_common_funcs = [func for func, count in function_counts.most_common(top_n_solutions)]
    else:
        most_common_funcs = list(function_counts.keys())

    # Für jeden eindeutigen Wert eine neue Spalte erstellen
    for func_name in most_common_funcs:
        column_name = f'count_{func_name}'
        df[column_name] = df['function_dir'].apply(lambda x: x.count(func_name))

    return df


def prepare_summary_df(df_total, df_better, df_worse, param):
    """
    Bereitet die Daten für die gestapelten Balken und Linien vor.
    """

    # Summe der gefundenen Lösungen pro Parameterwert und Gruppe
    def get_solutions_per_param(df, group_name):
        solutions_per_param = df.groupby(param)['count'].sum().reset_index()
        solutions_per_param.columns = [param, f'{group_name}_solutions']
        return solutions_per_param

    total_solutions = get_solutions_per_param(df_total, 'Total')
    better_solutions = get_solutions_per_param(df_better, 'Better')
    worse_solutions = get_solutions_per_param(df_worse, 'Worse')

    # Gesamtzahl der gefundenen Lösungen in jeder Gruppe
    total_solutions_sum = total_solutions['Total_solutions'].sum()
    better_solutions_sum = better_solutions['Better_solutions'].sum()
    worse_solutions_sum = worse_solutions['Worse_solutions'].sum()

    # Berechnung der relativen Häufigkeiten
    total_solutions['Total_percent'] = (total_solutions['Total_solutions'] / total_solutions_sum) * 100
    better_solutions['Better_percent'] = (better_solutions['Better_solutions'] / better_solutions_sum) * 100
    worse_solutions['Worse_percent'] = (worse_solutions['Worse_solutions'] / worse_solutions_sum) * 100

    # Zusammenführen der Daten
    summary_df = pd.merge(total_solutions, better_solutions, on=param, how='outer')
    summary_df = pd.merge(summary_df, worse_solutions, on=param, how='outer')

    # NaN-Werte mit 0 ersetzen
    summary_df = summary_df.fillna(0)

    # Segmente für die gestapelten Balken vorbereiten
    segments_df = prepare_segments_df(df_total, df_better, df_worse, param)

    return summary_df, segments_df


def prepare_segments_df(df_total, df_better, df_worse, param):
    """
    Bereitet die Segmente für die gestapelten Balken vor.
    """

    # Funktion zum Erstellen eines DataFrames mit den Segmenten
    def get_segments(df, group_name):
        segments = []
        for idx, row in df.iterrows():
            param_value = row[param]
            count = row['count']
            combination = row['parameter_combination']
            segments.append(
                {'param_value': param_value, 'combination': combination, 'count': count, 'group': group_name})
        return pd.DataFrame(segments)

    # Segmente für Gesamt, Besser und Schlechter erstellen
    total_segments = get_segments(df_total, 'Gesamt')
    better_segments = get_segments(df_better, 'Besser')
    worse_segments = get_segments(df_worse, 'Schlechter')

    # Alle Segmente zusammenführen
    all_segments = pd.concat([total_segments, better_segments, worse_segments], ignore_index=True)

    return all_segments


def plot_stacked_bars_with_lines(data_tuple, param, percentages_df, save_path=None, stats_df=None):
    """
    Erstellt gestapelte Balken und Linien für Lösungsnamen.

    - Fügt Fehlerbalken hinzu, um die Standardabweichung der 'count'-Metrik darzustellen.
    """
    # Mapping der Parameter auf die entsprechenden LaTeX-Symbole
    param_to_latex = {
        'regs': r'$r_{\text{free}}$',  # $\NfreeReg$
        'inst': r'$i_{\text{free}}$',  # $\NfreeInst$
        'popS': r'$\lambda$',  # Populationsgröße
        'gen': r'$G_{\text{max}}$',  # Maximale Generationenanzahl
        'mutInst': r'$\mu_{\text{I}}$',  # Instruktionsmutationsrate
        'mutRegs': r'$\mu_{\text{R}}$',  # Registermutationsrate
        'cross': r'$\rho$'  # Rekombinationsrate
    }

    summary_df, segments_df = data_tuple

    # Konvertieren der Parameterwerte in numerische Typen
    try:
        summary_df[param] = summary_df[param].astype(float)
        segments_df['param_value'] = segments_df['param_value'].astype(float)
        percentages_df.index = percentages_df.index.astype(float)
        if stats_df is not None:
            stats_df[param] = stats_df[param].astype(float)
    except ValueError:
        print(f"Warnung: Konnte Parameter '{param}' nicht in float konvertieren. Behandle ihn als kategorisch.")
        pass

    # Einzigartige Parameterwerte numerisch sortiert
    param_values = sorted(summary_df[param].unique())

    # Mapping von Parameterwerten zu Positionen
    param_value_to_position = {param_value: idx for idx, param_value in enumerate(param_values)}
    positions = [param_value_to_position[param_value] for param_value in param_values]

    fig, ax1 = plt.subplots(figsize=(7, 5))

    # Für jeden Parameterwert Balken erstellen
    bar_width = 0.2
    offsets = [-bar_width, 0, bar_width]
    groups = ['Gesamt', 'Besser', 'Schlechter']
    colors = {'Gesamt': 'skyblue', 'Besser': 'limegreen', 'Schlechter': 'salmon'}

    for offset, group in zip(offsets, groups):
        group_data = segments_df[segments_df['group'] == group]
        for param_value in param_values:
            bar_position = param_value_to_position[param_value] + offset
            param_group_data = group_data[group_data['param_value'] == param_value]
            if param_group_data.empty:
                continue
            bottom = 0
            for _, row in param_group_data.iterrows():
                ax1.bar(bar_position, row['count'], bottom=bottom, width=bar_width, color=colors[group],
                        edgecolor='grey')
                bottom += row['count']

    # Achsen und Titel einstellen
    ax1.set_xlabel(param_to_latex.get(param, param), fontweight='bold')
    ax1.set_ylabel('Anzahl der gefundenen Lösungen')
    ax1.set_xticks([param_value_to_position[param_value] for param_value in param_values])
    ax1.set_xticklabels([str(param_value) for param_value in param_values], rotation=45)

    # Fehlerbalken hinzufügen (Standardabweichung der 'count'-Metrik)
    if stats_df is not None:
        stats_df.sort_values(by=param, inplace=True)
        error_positions = [param_value_to_position.get(val, None) for val in stats_df[param]]
        y_values = stats_df['count_mean']
        y_errors = stats_df['count_std']

        # Remove any None values
        valid_indices = [i for i, pos in enumerate(error_positions) if pos is not None]
        error_positions = [error_positions[i] for i in valid_indices]
        y_values = [y_values.iloc[i] for i in valid_indices]
        y_errors = [y_errors.iloc[i] for i in valid_indices]

        ax1.errorbar(
            error_positions,
            y_values,
            yerr=y_errors,
            fmt='none',
            ecolor='black',
            capsize=5,
            label='Standardabweichung'
        )

    # Legende für Balken und Fehlerbalken
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors[group], label=group) for group in groups]
    legend_elements.append(Patch(facecolor='none', edgecolor='black', label='Standardabweichung'))

    # Linien für Lösungsnamen plotten
    ax2 = ax1.twinx()

    # Marker und Farben für Lösungsnamen definieren
    markers = ['o', 's', '^', 'D', 'v', '*', '+', 'x']
    line_styles = ['-', '--', '-.', ':']
    style_cycler = itertools.cycle(line_styles)
    marker_cycler = itertools.cycle(markers)

    for solution_name in percentages_df.columns:
        marker = next(marker_cycler)
        style = next(style_cycler)
        percentages = percentages_df[solution_name]

        # Sortieren der Daten entsprechend den sortierten Parameterwerten
        percentages = percentages.reindex(param_values, fill_value=0)

        # x-Positionen entsprechend den sortierten Parameterwerten
        x_positions = [param_value_to_position[param_value] for param_value in percentages.index]

        ax2.plot(
            x_positions,
            percentages.values,
            color='black',
            linestyle=style,
            marker=marker,
            label=solution_name
        )

    ax2.set_ylabel('Lösungsanzahl je Problem in den Besten 20%')

    # Legenden kombinieren
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    # Speichern als PDF, wenn der Pfad angegeben ist
    if save_path:
        save_name = os.path.join(save_path, f'{param}.pdf')
        plt.savefig(save_name, format='pdf')
        # plt.show()


def compute_statistics(df, param):
    """
    Berechnet Mittelwert und Standardabweichung der Metriken pro Parameterwert.
    """
    # Metriken, für die Statistiken berechnet werden sollen
    metrics = ['count', 'mean_found_generation', 'mean_start_diversity', 'mean_end_diversity']

    # Initialisiere ein leeres DataFrame
    stats_df = pd.DataFrame()

    for metric in metrics:
        # Gruppieren nach Parameterwert und Berechnung von Mittelwert und Standardabweichung
        grouped = df.groupby(param)[metric].agg(['mean', 'std']).reset_index()
        # Umbenennen der Spalten
        grouped.rename(columns={'mean': f'{metric}_mean', 'std': f'{metric}_std'}, inplace=True)
        # Zusammenführen der Ergebnisse
        if stats_df.empty:
            stats_df = grouped
        else:
            stats_df = pd.merge(stats_df, grouped, on=param, how='outer')

    # NaN-Werte mit 0 ersetzen
    stats_df.fillna(0, inplace=True)

    return stats_df


def main():
    # Pfad zu Ihrem Projektverzeichnis
    base_dir = os.path.join('C:\\', 'Users', 'Nick_', 'Programmieren', 'IdeaProjects', 'GeneticProgramming')
    os.chdir(base_dir)

    # Setze Pfad zur Datendatei
    log_dir = os.path.join('log', 'testdata', 'Vfinal')
    save_path = os.path.join(log_dir, 'testdaten_randomsearchVfinal_gefiltert_1e-11_plots_gen_100k')
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(save_path, exist_ok=True)
    test_dir = os.path.join(log_dir, "testdaten_randomsearchVfinal_gefiltert_1e-11.csv")

    # Daten einlesen
    df = read_data(test_dir)

    df = filter_data(df, 'gen == 100000')

    # Neue Methode aufrufen, um zusätzliche Spalten zu erstellen (Top 5 Lösungen)
    processed_df = process_additional_columns(df, top_n_solutions=5)
    print(processed_df['mean_found_generation'])

    # Median von 'count' berechnen und Daten aufteilen
    # m = 0  # Diesen Wert können Sie anpassen
    # better_df, worse_df, middle_df, median_count = split_by_count_median(processed_df, m)
    better_df, worse_df, lower, upper, median = split_by_combined_score_with_relative_generation(processed_df,
                                                                                                 lower_quantile=0.5,
                                                                                                 upper_quantile=0.8,
                                                                                                 count_weight=0.8,
                                                                                                 generation_weight=0.2)
    print(f"Median von 'combined_score': {median}")
    print(f"untere Grenze von 'combined_score': {lower}")
    print(f"obere Grenze von 'combined_score': {upper}")
    print(f"Anzahl der Zeilen im ursprünglichen DataFrame: {len(processed_df)}")
    print(f"Anzahl der Zeilen im 'better_df' (bessere Kombinationen): {len(better_df)}")
    print(f"Anzahl der Zeilen im 'worse_df' (schlechtere Kombinationen): {len(worse_df)}")

    # Überprüfen, ob die Gruppen nicht leer sind
    if better_df.empty or worse_df.empty:
        print("Eine der Gruppen ist leer. Bitte passen Sie den Wert von 'm' an oder überprüfen Sie die Daten.")
        return

    stats_df = compute_statistics(processed_df, 'regs')
    print(stats_df)
    # Analysen durchführen
    analyze_hyperparameters(processed_df, better_df, worse_df, save_path)


if __name__ == '__main__':
    main()
