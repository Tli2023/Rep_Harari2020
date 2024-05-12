import pandas as pd

data = pd.read_stata('/Users/tli/github/Rep_Harari2020/data/CityShape_Main.dta')
output = '/Users/tli/github/Rep_Harari2020/results/table1b.tex'
# housekeeping -------

# filter data 
data = data[data['insample_IV_5010'] == 1]
data.columns
data['year'] = data['year'].astype(int)

# Define the list of variables
mylist = ['area_polyg_km', 'disconnect_km', 'r1_relev_disconnect_cls_km', 'TOTAL_pop_all']

# Filter the data for years 1950 and 2010
data = data[data['year'].isin([1950, 2010])]
# Calculate sum statistics for year 1950
stats_1950 = data[data['year'] == 1950][mylist].describe().loc[['mean', 'std']].T.round(3)

# Calculate sum statistics for year 2010
stats_2010 = data[data['year'] == 2010][mylist].describe().loc[['mean', 'std']].T.round(3)

# Calculate the difference between 2010 and 1950 for each variable
df_diff = data[['id', 'year'] + mylist]

df_wide = df_diff.pivot(index='id', columns='year', values=mylist)

# Flatten the columns after pivoting
df_wide.columns = ['{}_{}'.format(var, year) for var, year in df_wide.columns]
df_wide
# Generate new variables based on the year differences 2010-1950
for var in mylist:
    df_wide[f'{var}_5010'] = df_wide[f'{var}_2010'] - df_wide[f'{var}_1950']

# Calculate sum statistics for the differences
diff_columns = [col for col in df_wide.columns if col.endswith('5010')]

# Calculate summary statistics for these columns
stats_diff = df_wide[diff_columns].describe().loc[['mean', 'std']].T.round(3)

# renaming
rename_dict = {
    'area_polyg_km_5010': 'Area, km2',
    'disconnect_km_5010': 'Shape, km',
    'r1_relev_disconnect_cls_km_5010': 'Potential shape, km',
    'TOTAL_pop_all_5010': 'City Population',
    'area_polyg_km': 'Area, km2',
    'disconnect_km': 'Shape, km',
    'r1_relev_disconnect_cls_km': 'Potential shape, km',
    'TOTAL_pop_all': 'City Population'
}

# Rename the indices
stats_diff.rename(index=rename_dict, inplace=True)
stats_1950.rename(index=rename_dict, inplace=True)
stats_2010.rename(index=rename_dict, inplace=True)


table = {
    "Description": ["Area, km2", "Shape, km", "Potential shape, km", "City Population"],
    "1950": [f"{mean_1950} ({std_1950})" for mean_1950, std_1950 in zip(stats_1950['mean'], stats_1950['std'])],
    "2010": [f"{mean_2010} ({std_2010})" for mean_2010, std_2010 in zip(stats_2010['mean'], stats_2010['std'])],
    "2010-1950": [f"{diff} ({std_diff})" for diff, std_diff in zip(stats_diff['mean'], stats_diff['std'])]
}

# Creating DataFrame
tabout = pd.DataFrame(table)

# Convert DataFrame to LaTeX code
latex_out = tabout.to_latex(index=False, escape=False, column_format="lccc", longtable=False)

# Write LaTeX code to a file
with open(output, 'w') as texfile:
    texfile.write(latex_out)

# end of the doc
