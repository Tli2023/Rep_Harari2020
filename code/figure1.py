# figure1.py
# last updated: May.10, 2024
# author: Tong LI
# code based on Harari(2020)

import pandas as pd
import numpy as np

resultsfolder = "/Users/tli/github/Rep_Harari2020/results"
data_path = "/Users/tli/github/Rep_Harari2020/data/CityShape_Main.dta"

data = pd.read_stata(data_path)

# Kolkata id = 457; Bangalore id = 150, We only want 2 cities in year 2005
filtered_data = data[data["year"] == 2005]
filtered_data = filtered_data[filtered_data["id"].isin([457, 150])]

filtered_data = filtered_data[["spin_km", "range_km", "remoteness_km", "disconnect_km", 
             "spin_N_km", "range_N_km", "remoteness_N_km", "disconnect_N_km", 
             "area_polyg_km", "id"]]

# creating EACradius 
filtered_data["NoN_EACradius"] = np.sqrt(filtered_data["area_polyg_km"] / np.pi)
filtered_data["Norm_EACradius"] = filtered_data["NoN_EACradius"]

# creating column prefixes to reshape in stata
prefixes = ["spin", "range", "remoteness", "disconnect"]
for var in filtered_data.columns:
    if any(var.startswith(prefix) for prefix in prefixes):
        stem = var.split("_")[0]
        if "_N_km" in var:
            filtered_data.rename(columns={var: f"Norm_{stem}"}, inplace=True)
        else:
            filtered_data.rename(columns={var: f"NoN_{stem}"}, inplace=True)


filtered_data.drop(columns=["area_polyg_km"], inplace=True)

# reshape long
reshaped_data = pd.melt(filtered_data, id_vars=['id'], var_name='variable', value_name='value')

# Create city indicator to reshape wide
reshaped_data['city'] = np.where(reshaped_data['id'] == 457, 'K',  # Kolkata
                                 np.where(reshaped_data['id'] == 150, 'B',  # Bangalore
                                          np.nan))

# Split the 'variable' column into 'type' and 'metric'
reshaped_data[['type', 'metric']] = reshaped_data['variable'].str.split('_', expand=True)

# reshape wide
wide_data = reshaped_data.pivot_table(index='metric', columns=['type', 'city'], values='value')

# Flatten the multi-level column index
wide_data.columns = ['_'.join(col).strip() for col in wide_data.columns.values]

# Reset the index
wide_data.reset_index(inplace=True)

# Pri# Get the 'NoN_K' value where 'metric' is 'EACradius'
K_area = wide_data.loc[wide_data['metric'] == 'EACradius', 'NoN_K'].values[0]

# Create 'NoN_rescale_B' column
wide_data['NoN_rescale_B'] = wide_data['Norm_B'] * K_area

# Generate new variables
wide_data['Adj_Diff'] = wide_data['NoN_K'] - wide_data['NoN_rescale_B']
wide_data['NoAdj_Diff'] = wide_data['NoN_K'] - wide_data['NoN_B']

# drop redundancy 
wide_data = wide_data[wide_data['metric'] != 'EACradius']

# Renaming each category in metrics
wide_data.loc[wide_data["metric"] == "disconnect", "metric"] = "1. Disconnection, km"
wide_data.loc[wide_data["metric"] == "remoteness", "metric"] = "2. Remoteness, km"
wide_data.loc[wide_data["metric"] == "spin", "metric"] = "3. Spin, km2"
wide_data.loc[wide_data["metric"] == "range", "metric"] = "4. Range, km"
# ordering
wide_data = wide_data[["metric", "NoN_K", "Norm_K", "NoN_B", "Norm_B"]].sort_values("metric")

# renaming to export 
wide_data.rename(columns={"metric": "Shape_Metric", "NoN_K": "NonNormMetric_Kolkata", "Norm_K": "Normalized_Kolkata", "NoN_B": "NonNormMetric_Bangalore", "Norm_B": "Normalized_Bangalore"}, inplace=True)
wide_data.to_excel(f"{resultsfolder}/Figure1.xlsx", index=False)

# end of the doc 