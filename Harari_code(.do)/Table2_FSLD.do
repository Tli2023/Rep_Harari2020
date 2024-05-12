version 13
cap restore
cap log close
clear all
set more off
set matsize 9000

*=================================================================================================*
** Set up
*=================================================================================================*


**********************************************************************************
************************************ Paths ***************************************
**********************************************************************************

global resultsfolder "/Users/tli/Desktop/replication_Harari/ReplicationFolder_Main/Out"
global datafoldernew "/Users/tli/Desktop/replication_Harari/ReplicationFolder_Main/data"
global logfolder 	"/Users/tli/Desktop/replication_Harari/ReplicationFolder_Main/log"

log using "${logfolder}/Table2_FSLD.log", replace 

**********************************************************************************
************************************ Tablesout ***********************************
**********************************************************************************

* Table 2: First stage, long difference (columns 1 and 2)
* Table2_Cols12_FS.xls

*=================================================================================================*
** Regressions
*=================================================================================================*

**********************************************************************************
********************************** Set up ****************************************
**********************************************************************************

use "$datafoldernew/CityShape_Main.dta", clear

* Sample: 351 cities
keep if insample_IV_5010==1

foreach var of varlist * { 
	local newname = subinstr("`var'","disconnect","d",.) 
	ren `var' `newname'
}


**********************************************************************************
***************** Reshape and generate log difference vars ***********************
**********************************************************************************

local diff 5010
local year1 1950 
local year2 2010

local mylist area_polyg_km d_N_km d_km  r1_relev_d_cls_km log_projected_pop log_area_polyg_km log_TOTAL_pop_all dens_core_all TOTAL_pop_all

keep id year `mylist'

foreach var of varlist `mylist' { 
	local newname = "`var'" + "_"
	ren `var' `newname' 
} 

reshape wide `mylist', i(id) j(year)

foreach j in `mylist' {
	gen `j'_5010=`j'_2010-`j'_1950
}

* Labels for regressions
label var d_km_5010	"D Shape, km"
label var log_area_polyg_km_5010 "D Log area"
label var log_projected_pop_5010 "D Log projected population"
label var r1_relev_d_cls_km_5010 "D Potential shape, km"


**********************************************************************************
********************************* First Stage ************************************
**********************************************************************************

************* Run xtivreg regression to get first stage F & KP stat ************

quie ivreg2 log_TOTAL_pop_all_5010  (d_km_5010 log_area_polyg_km_5010 = r1_relev_d_cls_km_5010 log_projected_pop_5010 )  , first cluster(id)

mat define fstat =e(first)
mat list fstat
quie local SWF_d_km=fstat[8,1]
quie local SWF_log_area_polyg_km=fstat[8,2]
quie local APF_d_km=fstat[15,1]
quie local APF_log_area_polyg_km=fstat[15,2]
qui local kptest=e(idstat)

local APF_d_km = round(`APF_d_km',.01)
local APF_d_km = substr("`APF_d_km'",1,strpos("`APF_d_km'",".")+2)
local APF_log_area_polyg_km = round(`APF_log_area_polyg_km',.01)
local APF_log_area_polyg_km = substr("`APF_log_area_polyg_km'",1,strpos("`APF_log_area_polyg_km'",".")+2)
qui local kptest = round(`kptest',.01)
local kptest = substr("`kptest'",1,strpos("`kptest'",".")+2)

**************************** First stage for shape *****************************

quie reg d_km_5010  r1_relev_d_cls_km_5010 log_projected_pop_5010, cluster(id)
outreg2 using "$resultsfolder/Table2_Cols12_FS.xls", nor2 nocons title(Table 2: First stage) addtext(AP F stat shape, "`APF_d_km'", AP F stat area, "`APF_log_area_polyg_km'" , KP test stat, "`kptest'") ctitle(OLS, Disconnection D2010-1950) label(insert) keep(r1_relev_d_cls_km_5010 log_projected_pop_5010 r1_relev_d_cls_km_5010 ) replace 

**************************** First stage for area *****************************

quie reg log_area_polyg_km_5010  r1_relev_d_cls_km_5010 log_projected_pop_5010, cluster(id)
outreg2 using "$resultsfolder/Table2_Cols12_FS.xls", nor2 nocons addtext(AP F stat shape, "`APF_d_km'", AP F stat area, "`APF_log_area_polyg_km'" , KP test stat, "`kptest'")  ctitle (OLS, Log area D2010-1950)  label(insert) keep( log_projected_pop_5010 r1_relev_d_cls_km_5010)   append 

**********************************************************************************
**********************************************************************************
**********************************************************************************
log close 
* end

