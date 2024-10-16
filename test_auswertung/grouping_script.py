# KI-Nutzungshinweis: dieser Codes wurde mithilfe von GPT-basierten KI-Tools generiert (o1-mini).
# KI-basierte und manuelle Anpassungen und Überarbeitungen wurden nachträglich durchgeführt.

import os
import pandas as pd

base_dir = os.path.join('C:\\', 'Users', 'Nick_', 'Programmieren', 'IdeaProjects', 'GeneticProgramming')
os.chdir(base_dir)

# Load the data
file_path = os.path.join('log', 'testdata', 'test_randomsearchV4_2_testdata.csv')
data = pd.read_csv(file_path, delimiter=';')

# Filter based on good_fitness and final_fitness > threshold
threshold = 1e-6
group_1 = data[data['good_fitness'] == True].copy()  # Use .copy() to avoid warnings
group_2 = data[data['final_fitness'] < threshold].copy()
group_3 = data.copy()

# Define the parameter columns to group by
parameter_columns = ['regs', 'inst', 'popS', 'gen', 'mutInst', 'mutRegs', 'cross']

# Add a count column before performing groupby
group_1['count'] = group_1.groupby(parameter_columns)[parameter_columns[0]].transform('size')
group_2['count'] = group_2.groupby(parameter_columns)[parameter_columns[0]].transform('size')
group_3['count'] = group_3.groupby(parameter_columns)[parameter_columns[0]].transform('size')

# Group by the parameter columns (excluding 'seed_dir') and aggregate other columns, but keep the count intact
group_1_grouped = group_1.groupby(parameter_columns).agg({'count': 'first', **{col: list for col in group_1.columns if col not in parameter_columns + ['count']}}).reset_index()
group_2_grouped = group_2.groupby(parameter_columns).agg({'count': 'first', **{col: list for col in group_2.columns if col not in parameter_columns + ['count']}}).reset_index()
group_3_grouped = group_3.groupby(parameter_columns).agg({'count': 'first', **{col: list for col in group_3.columns if col not in parameter_columns + ['count']}}).reset_index()

# Create a new column where parameters are concatenated as a single string
group_1_grouped['parameter_combination'] = group_1_grouped[parameter_columns].astype(str).agg('_'.join, axis=1)
group_2_grouped['parameter_combination'] = group_2_grouped[parameter_columns].astype(str).agg('_'.join, axis=1)
group_3_grouped['parameter_combination'] = group_3_grouped[parameter_columns].astype(str).agg('_'.join, axis=1)

# Output the results
print('Group 1 (good_fitness=True) grouped results:')
print(group_1_grouped)

print('Group 2 (final_fitness > threshold) grouped results:')
print(group_2_grouped)

# Save the grouped results to CSV files with semicolon as the delimiter
save_path = os.path.join('..', 'log', 'test_randomsearchV4_2', 'testdaten_randomsearchV4_2_gefiltert_1e-11.csv')
save_path2 = os.path.join('..', 'log', 'test_randomsearchV4_2', 'testdaten_randomsearchV4_2_gefiltert_1e-6.csv')
# save_path3 = os.path.join('log', 'testdata', 'testdaten_randomsearchV4_2_ungefiltert.csv')
group_1_grouped.to_csv(save_path, index=False, sep=';')
group_2_grouped.to_csv(save_path2, index=False, sep=';')
# group_3_grouped.to_csv(save_path3, index=False, sep=';')
