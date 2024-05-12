import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS


# Load data
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

# Prepare DataFrame for IV2SLS model
dependent = df_wide['log_TOTAL_pop_all_5010']
exog = None 
endog = df_wide[['d_km_5010', 'log_area_polyg_km_5010']]
instr = df_wide[['r1_relev_d_cls_km_5010', 'log_projected_pop_5010']]
df_wide.reset_index(inplace=True)

# Run the IV regression model
model = IV2SLS(dependent, exog, endog, instr)
results = model.fit(cov_type='clustered', clusters=df_wide['id'])
first_stage = results.first_stage
results.first_stage
# Print the results
print(results.summary)

# from the py.stats model documentation, I am not able to obtain KPF & APF stats. 
# https://bashtage.github.io/linearmodels/iv/examples/advanced-examples.html
# https://bashtage.github.io/linearmodels/iv/iv/linearmodels.iv.model.IV2SLS.html

# First Stage Reg. on d_km_5010
ols1 = smf.ols('d_km_5010 ~ r1_relev_d_cls_km_5010 + log_projected_pop_5010', hasconst=None, data=df_wide)
col1 = ols1.fit(cov_type='cluster', cov_kwds={'groups': df_wide['id']})
col1.summary()

# first satge reg. on log_area_polyg_km_5010
ols2= smf.ols(formula='log_area_polyg_km_5010 ~ r1_relev_d_cls_km_5010 + log_projected_pop_5010',hasconst=None, data=df_wide)
col2 = ols2.fit(cov_type='cluster', cov_kwds={'groups': df_wide['id']})
col2.summary()
# exporting the results:
out1 = pd.DataFrame({
    'Variable': col1.params.index,
    'Coef': col1.params.values,
    'Std Err': col1.bse.values,
    'Model': ['Disconnection D2010-1950'] * len(col1.params),
})

out2 = pd.DataFrame({
    'Variable': col2.params.index,
    'Coef': col2.params.values,
    'Std Err': col2.bse.values,
    'Model': ['Log area D2010-1950'] * len(col2.params),
})


# Concatenate results
output = pd.concat([out1, out2]).reset_index(drop=True)
variable_labels = {
    'd_km_5010': 'Δ Shape, km',
    'log_area_polyg_km_5010': 'Δ Log area',
    'log_projected_pop_5010': 'Δ Log projected population',
    'r1_relev_d_cls_km_5010': 'Potential shape, km',
}

output['Variable'] = output['Variable'].replace(variable_labels)

# Combine 'Coef' and 'Std Err' into one column
output['Coef (Std Err)'] = output['Coef'].map('{:.3f}'.format) + " (" + output['Std Err'].map('{:.3f}'.format) + ")"

# Prepare final table for LaTeX
output = output[['Model', 'Variable', 'Coef (Std Err)']]
output2 = output.pivot(index='Variable', columns='Model', values='Coef (Std Err)').reset_index()

latout = output2.to_latex(index=False, escape=False, column_format="llcr", longtable=False, multirow=True)

outpath = '/Users/tli/github/Rep_Harari2020/results/table2_FSLD.tex'
# save to a file
with open(outpath, "w") as file:
    file.write(latout)

# this is the output for table 2a. 
#---------------------------------#
