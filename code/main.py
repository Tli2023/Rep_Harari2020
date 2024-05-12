# main.py 
# this is the master code that will run the entire program
# code based on Harari(2020)
# date created: May.10, 2024
# author:  Tong LI

import pandas as pd

# global codepath
codepath = "/Users/tli/github/Rep_Harari2020/code"

# reproducing figure 1: 
figure1 = f'{codepath}/figure1.py'
with open(figure1, 'r') as f:
    exec(f.read())

# reproducing table 1b:
table1b = f'{codepath}/table1b.py'
with open(table1b, 'r') as f:
    exec(f.read())

# reproducing table 2 log difference:
table2a = f'{codepath}/table2_FSLD.py'
with open(table2a, 'r') as f:
    exec(f.read())

# reproducing table 2 panel level:
table2b = f'{codepath}/table2_FSPanel.py'
with open(table2b, 'r') as f:
    exec(f.read())

# reproducing table 3 IV:
table3 = f'{codepath}/table3_PopulationLD.py'
with open(table3, 'r') as f:
    exec(f.read())

# Reproducing Table 6 Iv with controls:
table6 = f'{codepath}/table6_IVRobustTrends.py'
with open(table6, 'r') as f:
    exec(f.read())  