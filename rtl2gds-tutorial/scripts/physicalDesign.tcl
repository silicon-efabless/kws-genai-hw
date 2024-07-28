
source "../scripts/helpers.tcl"
source "../scripts/flow_helpers.tcl"
source "../sky130hd/sky130hd.vars"

set synth_verilog "../pd/synth.v"
set design "counter"
set top_module "counter"
set sdc_file "../scripts/top.sdc"

# if 0 is used to multiline comment
#---------Bigger design core and die---------
if 0 {
set die_area {0 0 299.96 300.128}
set core_area {9.996 10.08 289.964 290.048}
}
#-------- design specific----------------

#if 0 {
set die_area {0 0 100.00 100.00}
set core_area {10.00 10.00 90.00 90.00}
#}

#------------Entire flow---------------------
source -echo "../scripts/flow.tcl"

#--The entire flow is divided into follwing subflows foe better visualization of steps--:
#---------floorplan-----------
#source -echo "flow_1_floorplan.tcl"

#-------Power distribution network--------
#source -echo "flow_2_pdn.tcl"

#-------Global placement----------------
#source -echo "flow_3_global_placement.tcl"

#-------Detailed placement--------------
#source -echo "flow_4_detailed_placement.tcl"

#-------Clock tree synthesis----------
#source -echo "flow_5_clockTreeSynthesis.tcl"

#-------Global Routing and detailed Routing------
#source -echo "flow_6_Routing.tcl"
