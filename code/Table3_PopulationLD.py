import pandas as pd
import numpy as np
from linearmodels.iv import IV2SLS
import statsmodels.formula.api as smf

# Caveat: as stressed, It is not possible to call KPW and APF stats from the 2sls package.
# https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html
# effect of 1SD increase in normalized shape on population has been omitted as it is not included in the final output table


# reshape wide 
df = pd.read_stata('/Users/tli/github/Rep_Harari2020/data/CityShape_Main.dta')
df = df[df['insample_IV_5010'] == 1]

# Variable renaming by replacing 'disconnect' with 'd'
df.columns = df.columns.str.replace('disconnect', 'd')

# List of variables for analysis
vars_list = [
    'area_polyg_km', 'd_N_km', 'd_km', 'r1_relev_d_cls_km',
    'log_projected_pop', 'log_area_polyg_km', 'log_TOTAL_pop_all', 
    'dens_core_all', 'TOTAL_pop_all'
]

# Keep relevant data
df = df[['id', 'year'] + vars_list]
df['year'] = df['year'].astype(int)

# by all means I only need 2 year: 1950 and 2010 to run the log dif model: 
# Reshape from long to wide format
df_wide = df.pivot(index='id', columns='year', values=vars_list).sort_index(level=1, axis=1)

# Flatten multi-index columns after pivoting
df_wide.columns = ['{}_{}'.format(var, year) for var, year in df_wide.columns]

# Generate log difference vars
for var in vars_list:
    df_wide[f'{var}_5010'] = df_wide[f'{var}_2010'] - df_wide[f'{var}_1950']

# running IV2SLS model
dependent = df_wide['log_TOTAL_pop_all_5010']
exog = None 
endog = df_wide[['d_km_5010', 'log_area_polyg_km_5010']]
instr = df_wide[['r1_relev_d_cls_km_5010', 'log_projected_pop_5010']]
df_wide.reset_index(inplace=True)

# Run the IV regression model
iv = IV2SLS(dependent, exog, endog, instr)
riv = iv.fit(cov_type='clustered', clusters=df_wide['id'])

# run the ols specification:
ols = smf.ols('log_TOTAL_pop_all_5010 ~ d_km_5010 + log_area_polyg_km_5010', data=df_wide)
rols = ols.fit(cov_type='cluster', cov_kwds={'groups': df_wide['id']})

# export to latex:
out1 = pd.DataFrame({
    'Variable': riv.params.index,
    'Coef': riv.params.values,
    'Std Err': riv.std_errors.values,
    'Model': ['IV2SLS D2010-1950'] * len(riv.params),
})

out2 = pd.DataFrame({
    'Variable': rols.params.index,
    'Coef': rols.params.values,
    'Std Err': rols.bse.values,
    'Model': ['OLS D2010-1950'] * len(rols.params),
})

output = pd.concat([out1, out2]).reset_index(drop=True)
variable_labels = {
    'd_km_5010': 'Δ Shape, km',
    'log_area_polyg_km_5010': 'Δ Log area',
    'log_projected_pop_5010': 'Δ Log projected population',
    'r1_relev_d_cls_km_5010': 'Potential shape, km',
    'Intercept': 'Intercept'
}
output['Variable'] = output['Variable'].replace(variable_labels)
output['Coef (Std Err)'] = output['Coef'].map('{:.3f}'.format) + " (" + output['Std Err'].map('{:.3f}'.format) + ")"
output = output[['Model', 'Variable', 'Coef (Std Err)']]
output2 = output.pivot(index='Variable', columns='Model', values='Coef (Std Err)').reset_index()
output2.fillna('-', inplace=True)

latout = output2.to_latex(index=False, escape=False, column_format="llcr", longtable=False, multirow=True)

outpath = '/Users/tli/github/Rep_Harari2020/results/table3_PopulationLD.tex'
# save to a file
with open(outpath, "w") as file:
    file.write(latout)

# end of the doc 