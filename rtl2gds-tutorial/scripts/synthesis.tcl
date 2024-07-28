# read design
read_verilog ../rtl/counter.v


# elaborate design hierarchy
hierarchy -check -top counter

# the high-level stuff
proc; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# mapping flip-flops to mycells.lib
dfflibmap -liberty ../sky130hd/sky130hd_tt.lib

# mapping logic to mycells.lib
abc -liberty ../sky130hd/sky130hd_tt.lib


# cleanup
clean

# write synthesized design
write_verilog -noattr ../pd/synth.v
