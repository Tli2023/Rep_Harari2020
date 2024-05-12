import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS

# An important caveat: as 2sls packages does not provide the KPF and APF stats, ( as shown in the table2_FSLD.py) 
# I will not be able to provide the KPF and APF stats, and thus for time efficiency, I will not run the IV2SLS model.
# https://bashtage.github.io/linearmodels/iv/examples/advanced-examples.html （source of the information)

df = pd.read_stata('/Users/tli/github/Rep_Harari2020/data/CityShape_Main.dta')
df = df[df['insample_IV_5010'] == 1]

df['year'] = df['year'].astype(int)
df = df.set_index(['id', 'year'])
# running the ols first stage on level reg for shape: 
shape = PanelOLS.from_formula('disconnect_km ~ log_projected_pop + r1_relev_disconnect_cls_km + EntityEffects + TimeEffects', data=df)
res_shape = shape.fit(cov_type='clustered', cluster_entity=True)

# running the ols first stage on level reg for area:
area =  PanelOLS.from_formula('log_area_polyg_km ~ log_projected_pop + r1_relev_disconnect_cls_km + EntityEffects + TimeEffects', data=df)
res_area = area.fit(cov_type='clustered', cluster_entity=True)
res_shape
# exporting to latex
data1 = {
    "Variable": res_shape.params.index.tolist(),
    "Coef": res_shape.params.values,
    "Std Err": res_shape.std_errors.values,
    "Model": ["Shape Panel"] * len(res_shape.params)
}

# Create a DataFrame with the extracted data
shape = pd.DataFrame(data1)

data2 = {
    "Variable": res_area.params.index.tolist(),
    "Coef": res_area.params.values,
    "Std Err": res_area.std_errors.values,
    "Model": ["Area Panel"] * len(res_area.params)
}

area = pd.DataFrame(data2)

# Append area and shape DataFrames
output = pd.concat([ area, shape]).reset_index(drop=True)

# rename columns
variable_labels = {
    'log_projected_pop': 'Log projected population',
    'r1_relev_disconnect_cls_km': 'Potential shape, km',
}
# Replace variable names with variable labels
output['Variable'] = output['Variable'].replace(variable_labels)
# Combine 'Coef' and 'Std Err' into one column
output['Coef (Std Err)'] = output['Coef'].map('{:.3f}'.format) + " (" + output['Std Err'].map('{:.3f}'.format) + ")"
output = output[['Model', 'Variable', 'Coef (Std Err)']]
output2 = output.pivot(index='Variable', columns='Model', values='Coef (Std Err)').reset_index()
output2.fillna('-', inplace=True)
latout = output2.to_latex(index=False, escape=False, column_format="llcr", longtable=False, multirow=True)

outpath = '/Users/tli/github/Rep_Harari2020/results/table2_FSPanel.tex'

# export
with open(outpath, "w") as file:
    file.write(latout)