# table 6: IV robust trends
import pandas as pd
import numpy as np
from linearmodels.iv import IV2SLS
import pandas as pd

df = pd.read_stata('/Users/tli/github/Rep_Harari2020/data/CityShape_Main.dta')
df = df[df['insample_IV_5010'] == 1]
df['year'] = df['year'].astype(int)

# Variable renaming by replacing 'disconnect' with 'd'
df.columns = df.columns.str.replace('disconnect', 'd')

df['elevation'] = df['elevation_m'] / 100
df.drop(columns=['elevation_m'], inplace=True)

vars_list = [
    'area_polyg_km', 'd_N_km', 'd_km', 'r1_relev_d_cls_km',
    'log_projected_pop', 'log_area_polyg_km', 'log_TOTAL_pop_all']

controls = ['elevation', 'coast_dist_km', 'dist_riverorlake', 'distance_mineral_km',
    'ROUGH', 'bedrockdepth', 'average_suit'
    ]

main = df[['id', 'year'] + vars_list]
df2 = df[['id', 'year'] + controls]
df2 = df2[df2['year'] == 2010] 

# Reshape from long to wide format
df_wide = main.pivot(index='id', columns='year', values=vars_list).sort_index(level=1, axis=1)

# Flatten multi-index columns after pivoting
df_wide.columns = ['{}_{}'.format(var, year) for var, year in df_wide.columns]

# Generate log difference vars
for var in vars_list:
    df_wide[f'{var}_5010'] = df_wide[f'{var}_2010'] - df_wide[f'{var}_1950']

# Drop variables that do not end with '_5010'
df_wide = df_wide[df_wide.columns[df_wide.columns.str.endswith('_5010')]]

# merge with the control variables (constant over time)
dfiv = df_wide.merge(df2, on='id', how='left')
dfiv['const'] = 1
dfiv.reset_index(inplace=True)

# loop to run the 2sls
dependent = dfiv['log_TOTAL_pop_all_5010']
endog = dfiv[['d_km_5010', 'log_area_polyg_km_5010']]
instr = dfiv[['r1_relev_d_cls_km_5010', 'log_projected_pop_5010']]

# Run the IV regression model
controlset = ['elevation', 'coast_dist_km', 'dist_riverorlake', 'distance_mineral_km',
                  'ROUGH', 'bedrockdepth', 'average_suit']


output = pd.DataFrame()

for var in controlset:
    # iv
    exog = dfiv[['const', f'{var}']] 
    iv = IV2SLS(dependent, exog, endog, instr)
    riv = iv.fit(cov_type='clustered', clusters=dfiv['id'])
    # Store the results in a DataFrame
    out1 = pd.DataFrame({
        'Variable': riv.params.index,
        'Coef': riv.params.values,
        'Std Err': riv.std_errors.values,
        'P-values': riv.pvalues.values,
        'Model': [f'IV2SLS {var} D2010-1950'] * len(riv.params)
    })
    # Append 
    output = pd.concat([output, out1]).reset_index(drop=True)

variable_labels = {
    'd_km_5010': 'Δ Shape, km',
    'log_area_polyg_km_5010': 'Δ Log area',
    'log_projected_pop_5010': 'Δ Log projected population',
    'r1_relev_d_cls_km_5010': 'Potential shape, km',
}

output['Variable'] = output['Variable'].replace(variable_labels)
output['Coef (Std Err)'] = output['Coef'].map('{:.3f}'.format) + " (" + output['Std Err'].map('{:.3f}'.format) + ")"
output = output[['Model', 'Variable', 'Coef (Std Err)']]
# bysort model export to latex 
newout = output.copy()
newout['Variable'] = newout['Variable'].apply(lambda x: 'Control' if x not in ['const', 'Δ Shape, km', 'Δ Log area'] else x)
newout = newout.pivot(index='Variable', columns='Model', values='Coef (Std Err)').reset_index()
latex_table = newout.to_latex(index=False, header=True, column_format='l' + 'c' * 7, escape=False)

# export
outpath = '/Users/tli/github/Rep_Harari2020/results/table6_IVRobustTrend.tex'
with open(outpath, 'w') as file:
    file.write(latex_table)

# end of the doc