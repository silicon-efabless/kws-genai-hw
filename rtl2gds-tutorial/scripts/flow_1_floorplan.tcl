# Assumes flow_helpers.tcl has been read.
read_libraries
read_verilog $synth_verilog
link_design $top_module
read_sdc $sdc_file

utl::metric "IFP::ord_version" [ord::openroad_git_describe]
# Note that sta::network_instance_count is not valid after tapcells are added.
utl::metric "IFP::instance_count" [sta::network_instance_count]

initialize_floorplan -site $site \
  -die_area $die_area \
  -core_area $core_area
insert_tiecells sky130_fd_sc_hd__conb_1/HI -prefix "TIE_ONE_"
insert_tiecells sky130_fd_sc_hd__conb_1/LO -prefix "TIE_ZERO_"
source $tracks_file
write_def ./lc_fp.def
# remove buffers inserted by synthesis
remove_buffers

################################################################
# IO Placement (random)
place_pins -random -hor_layers $io_placer_hor_layer -ver_layers $io_placer_ver_layer

################################################################
# Macro Placement
if { [have_macros] } {
  global_placement -density $global_place_density
  macro_placement -halo $macro_place_halo -channel $macro_place_channel
}

################################################################
# Tapcell insertion
eval tapcell $tapcell_args

set floorplan_db [make_result_file ${design}_${platform}_floorplan.odb]
write_db $floorplan_db


