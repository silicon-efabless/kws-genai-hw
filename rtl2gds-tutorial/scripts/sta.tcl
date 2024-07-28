# instructs OpenSTA to read and load liberty file
read_liberty ../sky130hd/sky130hd_tt.lib
# instructs OpenSTA to read and load the netlist
read_verilog ../pd/synth.v
# Using "top," which stands for the main module, links the Verilog code with the Liberty timing 
link_design counter
#Reads and loads the Synopsys Design Constraints (SDC) file "top.sdc"
read_sdc ../scripts/top.sdc
report_checks -path_delay max -format full
#Report of the timing checks for the design (setup)
#report_checks -path_delay max > reports.txt
#Store the report of the timing checks for the design (setup) in the reports.txt file.
report_checks -path_delay min -format full
#Report of the timing checks for the design (hold)
#report_checks -path_delay min > reports.txt
#Store the report of the timing checks for the design (hold) in the reports.txt file.
