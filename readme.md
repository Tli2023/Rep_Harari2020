# README
This document explains what has been modified and what is contained in this repository.

Last update: May.12.2024
Author: Tong LI

link to repo: https://github.com/Tli2023/Rep_Harari2020

# Explaination of the Code Structure:
## code/
This is the folder where my replication code rests.
==code/main.py==
This is the main programme, it executes all replication py codes.

* code/figure1.py
  This is the python code based on `Harari_code/figure1.do` to reproduce figure 1 in Harari(2020)
* code/table1b.py
  This is the python code based on `Harari_code/Table1B_SumStatsLD.do` to reproduce Table 1b in Harari(2020)
* code/table2_FSLD.py
  This is the python code based on `Harari_code/Table2_FSLD.do` to reproduce table 2 column 1 & 2 in Harari(2020)
* code/table2_FSPanel.py
  This is the python code based on `Harari_code/Table2_FSPanel.do` to reproduce table 2 column 3 & 4 in Harari(2020)
* code/Table3_PopulationLD.py
   This is the python code based on `Harari_code/Table3_PopulationLD.do` to reproduce table 3 in Harari(2020)
* code/Table6_IVRobustTrends.py
   This is the python code based on `Harari_code/Table6_IVRobustTrends.do` to reproduce table 3 in Harari(2020)

## data/
This folder the data file from Harari(2020). It is the cleaned data after all data cleaning process. 
* CityShape_Main.dta reproduce data in the main paper

All Replication codes and Harari's original code are based on this dta.

## Results/
This folder contains the output from running code/, each output is named wrt to the code that produces it.

## Harari_code/
This folder contains all Harari's original code on STATA as a reference. 

# What codes are choose to be replicated under `code/` ? 
* Figure1: 
  * One of the main contribution of Harari is to calculate the compactness of each city. Unfortunately all of the map and polygon figures are not disclosed under her replication package. Figure1.do only reproduces the table stats other than the shape polygons. I would assume she created by some vector tools in her pre-preliminary gis processing stage. Similarily, I am not able to replicate how she created her instruments graphically, as it is also not included in her replication readme.pdf. 
  * the result is stored in `results/figure1.xlsx`
* Table1b:
  * I think it is more rational to review the panel data by year used in regressions. Thus I only replicate 1b as it is more important than 1a. 
* Table2:
  * I reproduce both the log difference first stage and level first stage regression. A major caveat is I am not able to obtain the APF and KPF stats via `linearmodels` and `statsmodels` package based on the documentation. Furthermore, python does not recognized the log difference model, where even noconstant is specified, it still reports with intercept in the first stage log-difference specifications.
* Table 3:
  * This is the key result from the paper. It shows the second stage IV coef. 
* Table 6:
  * One threat to identification is that the city expantion is subjected to geographic characteristics. To control from it, the author includes 7 geographic characteristics, to make sure the IV result is robust. 

*end of the document*