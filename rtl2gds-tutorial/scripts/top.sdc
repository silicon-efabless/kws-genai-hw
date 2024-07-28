create_clock -name CLK -period 1000 [get_ports clk]

set_input_delay 0 -clock CLK [get_ports in]

set_output_delay 0 -clock CLK [get_ports y] 
